#!/usr/bin/env python3
"""
generate_assets.py — builds every static / seed asset for ActionLK Breach
from secrets.env, so the whole box stays internally consistent.

Run this ONCE after editing secrets.env, from the project root:

    python3 scripts/generate_assets.py

Requires only Python 3 stdlib + Pillow (`pip install pillow`).
Produces:
  static-challenges/stage1-public-trail/profile.jpg
  static-challenges/stage2-encoded-note/encoded_note.txt
  static-challenges/stage4-sniffing-the-wire/capture.pcap
  static-challenges/stage6-the-vault/vault_backup.zip.enc   (+ copy into stage5)
  stage5-behindthedoor/files/readme.txt
  stage5-behindthedoor/files/admin_notes.txt
"""
import base64
import os
import struct
import subprocess
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_env(path):
    env = {}
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip()
    return env


ENV = load_env(ROOT / "secrets.env")


def caesar(text, shift):
    out = []
    for ch in text:
        if ch.isupper():
            out.append(chr((ord(ch) - 65 + shift) % 26 + 65))
        elif ch.islower():
            out.append(chr((ord(ch) - 97 + shift) % 26 + 97))
        else:
            out.append(ch)
    return "".join(out)


# ---------------------------------------------------------------------------
# Stage 1 — image with a note hidden in the JPEG COM (Comment) segment,
# the field exiftool reports as "Comment".
# ---------------------------------------------------------------------------
def build_stage1():
    from PIL import Image, ImageDraw

    out_dir = ROOT / "static-challenges" / "stage1-public-trail"
    out_dir.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGB", (600, 400), (24, 34, 58))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, 600, 90], fill=(15, 22, 40))
    draw.text((24, 30), "ActionLK — Team Profile", fill=(230, 230, 230))
    draw.ellipse([250, 140, 350, 240], outline=(120, 160, 220), width=4)
    draw.text(
        (200, 260),
        f"{ENV['STAGE1_EMPLOYEE_FIRST']} {ENV['STAGE1_EMPLOYEE_SURNAME']}",
        fill=(220, 220, 220),
    )
    draw.text((200, 285), "Employee Engagement Team", fill=(150, 160, 180))

    raw_path = out_dir / "_profile_raw.jpg"
    img.save(raw_path, "JPEG", quality=88)

    # Insert a JPEG COM (0xFFFE) marker segment right after the SOI marker
    # (0xFFD8) so `exiftool profile.jpg` reports it under the "Comment" tag.
    comment_text = (
        f"Note to self ({ENV['STAGE1_EMPLOYEE_FIRST']} "
        f"{ENV['STAGE1_EMPLOYEE_SURNAME']}): forgot to strip this before "
        f"uploading. Flag: {ENV['STAGE1_FLAG']}"
    ).encode("utf-8")

    data = raw_path.read_bytes()
    assert data[:2] == b"\xff\xd8", "unexpected JPEG header"

    seg_len = len(comment_text) + 2  # length field includes itself
    com_segment = b"\xff\xfe" + struct.pack(">H", seg_len) + comment_text

    final_path = out_dir / "profile.jpg"
    final_path.write_bytes(data[:2] + com_segment + data[2:])
    raw_path.unlink()
    print(f"[stage1] wrote {final_path} ({final_path.stat().st_size} bytes)")


# ---------------------------------------------------------------------------
# Stage 2 — Base64(Caesar(flag))
# ---------------------------------------------------------------------------
def build_stage2():
    out_dir = ROOT / "static-challenges" / "stage2-encoded-note"
    out_dir.mkdir(parents=True, exist_ok=True)

    shift = int(ENV["STAGE2_CAESAR_SHIFT"])
    shifted = caesar(ENV["STAGE2_FLAG"], shift)
    encoded = base64.b64encode(shifted.encode("utf-8")).decode("ascii")

    path = out_dir / "encoded_note.txt"
    path.write_text(encoded + "\n")
    print(f"[stage2] wrote {path} -> {encoded}")


# ---------------------------------------------------------------------------
# Stage 4 — a hand-crafted pcap: TCP handshake + a plaintext FTP login,
# built without scapy so it needs nothing beyond the stdlib.
# ---------------------------------------------------------------------------
def ip_checksum(header: bytes) -> int:
    if len(header) % 2:
        header += b"\x00"
    total = sum(struct.unpack("!%dH" % (len(header) // 2), header))
    while total >> 16:
        total = (total & 0xFFFF) + (total >> 16)
    return (~total) & 0xFFFF


def tcp_checksum(src_ip, dst_ip, tcp_header_and_payload: bytes) -> int:
    pseudo = struct.pack(
        "!4s4sBBH",
        src_ip,
        dst_ip,
        0,
        6,  # TCP protocol number
        len(tcp_header_and_payload),
    )
    return ip_checksum(pseudo + tcp_header_and_payload)


class TcpStreamBuilder:
    """Builds a sequence of raw Ethernet/IPv4/TCP frames for one TCP stream."""

    def __init__(self, client, server, client_mac, server_mac):
        self.c_ip, self.c_port = client
        self.s_ip, self.s_port = server
        self.c_mac, self.s_mac = client_mac, server_mac
        self.c_seq = 1000
        self.s_seq = 5000
        self.ts = 1_732_000_000.0
        self.packets = []

    def _frame(self, src_mac, dst_mac, src_ip, dst_ip, sport, dport,
               seq, ack, flags, payload=b""):
        ip_ver_ihl = 0x45
        total_len = 20 + 20 + len(payload)
        ip_header_no_csum = struct.pack(
            "!BBHHHBBH4s4s",
            ip_ver_ihl, 0, total_len, 0x1234, 0, 64, 6, 0,
            src_ip, dst_ip,
        )
        csum = ip_checksum(ip_header_no_csum)
        ip_header = struct.pack(
            "!BBHHHBBH4s4s",
            ip_ver_ihl, 0, total_len, 0x1234, 0, 64, 6, csum,
            src_ip, dst_ip,
        )

        data_offset = (5 << 4)
        window = 65535
        tcp_no_csum = struct.pack(
            "!HHIIBBHHH",
            sport, dport, seq, ack, data_offset, flags, window, 0, 0,
        ) + payload
        t_csum = tcp_checksum(src_ip, dst_ip, tcp_no_csum)
        tcp_header = struct.pack(
            "!HHIIBBHHH",
            sport, dport, seq, ack, data_offset, flags, window, t_csum, 0,
        )

        eth = struct.pack("!6s6sH", bytes.fromhex(dst_mac.replace(":", "")),
                           bytes.fromhex(src_mac.replace(":", "")), 0x0800)
        pkt = eth + ip_header + tcp_header + payload
        self.ts += 0.05
        self.packets.append(pkt)

    # TCP flag bits
    FIN, SYN, ACK, PSH = 0x01, 0x02, 0x10, 0x08

    def handshake(self):
        self._frame(self.c_mac, self.s_mac, self.c_ip, self.s_ip,
                    self.c_port, self.s_port, self.c_seq, 0, self.SYN)
        self.s_seq_base = self.s_seq
        self._frame(self.s_mac, self.c_mac, self.s_ip, self.c_ip,
                    self.s_port, self.c_port, self.s_seq, self.c_seq + 1,
                    self.SYN | self.ACK)
        self.c_seq += 1
        self.s_seq += 1
        self._frame(self.c_mac, self.s_mac, self.c_ip, self.s_ip,
                    self.c_port, self.s_port, self.c_seq, self.s_seq,
                    self.ACK)

    def server_says(self, text):
        payload = text.encode("ascii")
        self._frame(self.s_mac, self.c_mac, self.s_ip, self.c_ip,
                    self.s_port, self.c_port, self.s_seq, self.c_seq,
                    self.PSH | self.ACK, payload)
        self.s_seq += len(payload)
        self._frame(self.c_mac, self.s_mac, self.c_ip, self.s_ip,
                    self.c_port, self.s_port, self.c_seq, self.s_seq,
                    self.ACK)

    def client_says(self, text):
        payload = text.encode("ascii")
        self._frame(self.c_mac, self.s_mac, self.c_ip, self.s_ip,
                    self.c_port, self.s_port, self.c_seq, self.s_seq,
                    self.PSH | self.ACK, payload)
        self.c_seq += len(payload)
        self._frame(self.s_mac, self.c_mac, self.s_ip, self.c_ip,
                    self.s_port, self.c_port, self.s_seq, self.c_seq,
                    self.ACK)

    def teardown(self):
        self._frame(self.c_mac, self.s_mac, self.c_ip, self.s_ip,
                    self.c_port, self.s_port, self.c_seq, self.s_seq,
                    self.FIN | self.ACK)
        self.c_seq += 1
        self._frame(self.s_mac, self.c_mac, self.s_ip, self.c_ip,
                    self.s_port, self.c_port, self.s_seq, self.c_seq,
                    self.FIN | self.ACK)
        self.s_seq += 1
        self._frame(self.c_mac, self.s_mac, self.c_ip, self.s_ip,
                    self.c_port, self.s_port, self.c_seq, self.s_seq,
                    self.ACK)

    def write_pcap(self, path):
        global_header = struct.pack(
            "<IHHiIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1
        )
        with open(path, "wb") as f:
            f.write(global_header)
            t = 1_732_000_000
            usec = 0
            for pkt in self.packets:
                f.write(struct.pack("<IIII", t, usec, len(pkt), len(pkt)))
                f.write(pkt)
                usec += 50000
                if usec >= 1_000_000:
                    t += 1
                    usec -= 1_000_000


def ipv4(s):
    return bytes(int(o) for o in s.split("."))


def build_stage4():
    out_dir = ROOT / "static-challenges" / "stage4-sniffing-the-wire"
    out_dir.mkdir(parents=True, exist_ok=True)

    b = TcpStreamBuilder(
        client=(ipv4("192.168.56.20"), 51000),
        server=(ipv4("192.168.56.30"), 21),
        client_mac="08:00:27:11:22:33",
        server_mac="08:00:27:aa:bb:cc",
    )
    b.handshake()
    b.server_says("220 ActionLK Internal File Service ready.\r\n")
    b.client_says(f"USER {ENV['STAGE4_FTP_USER']}\r\n")
    b.server_says("331 Please specify the password.\r\n")
    b.client_says(f"PASS {ENV['STAGE4_FTP_PASSWORD']}\r\n")
    b.server_says("230 Login successful.\r\n")
    b.client_says("SYST\r\n")
    b.server_says("215 UNIX Type: L8\r\n")
    b.client_says("QUIT\r\n")
    b.server_says("221 Goodbye.\r\n")
    b.teardown()

    path = out_dir / "capture.pcap"
    b.write_pcap(path)
    print(f"[stage4] wrote {path} ({len(b.packets)} packets)")


# ---------------------------------------------------------------------------
# Stage 5 supporting files + Stage 6 encrypted vault (needs openssl on PATH)
# ---------------------------------------------------------------------------
def build_stage5_and_6():
    s5_files = ROOT / "stage5-behindthedoor" / "files"
    s5_files.mkdir(parents=True, exist_ok=True)

    (s5_files / "readme.txt").write_text(
        "Your own backups. Nothing interesting here — try another user_id?\n"
    )
    (s5_files / "admin_notes.txt").write_text(
        "Internal note: vault_backup.zip.enc is the encrypted export the "
        "fraud team pulled before the outage.\n"
        f"Partial credit flag: {ENV['STAGE5_PARTIAL_FLAG']}\n"
    )

    # Build the vault contents: a small zip with the final flag inside.
    work = ROOT / "scripts" / "_vault_tmp"
    work.mkdir(exist_ok=True)
    flag_file = work / "incident_report_final.txt"
    flag_file.write_text(
        "CERT-SL Incident Report — Final Artefact\n"
        "=========================================\n"
        f"{ENV['STAGE6_FLAG']}\n"
    )
    zip_path = work / "vault_backup.zip"
    if zip_path.exists():
        zip_path.unlink()
    subprocess.run(
        ["zip", "-j", str(zip_path), str(flag_file)],
        check=True, cwd=work, stdout=subprocess.DEVNULL,
    )

    enc_path_s6 = ROOT / "static-challenges" / "stage6-the-vault" / "vault_backup.zip.enc"
    subprocess.run(
        [
            "openssl", "enc", "-aes-256-cbc", "-salt", "-pbkdf2",
            "-in", str(zip_path),
            "-out", str(enc_path_s6),
            "-k", ENV["STAGE6_PASSPHRASE"],
        ],
        check=True,
    )
    # Same file is also what the Stage 5 IDOR "leaks" thematically.
    enc_path_s5 = s5_files / "vault_backup.zip.enc"
    enc_path_s5.write_bytes(enc_path_s6.read_bytes())

    for p in (flag_file, zip_path):
        p.unlink()
    work.rmdir()

    print(f"[stage5/6] wrote {enc_path_s6} and copy in stage5-behindthedoor/files/")


def main():
    build_stage1()
    build_stage2()
    build_stage4()
    build_stage5_and_6()
    print("\nAll assets generated from secrets.env.")


if __name__ == "__main__":
    main()
