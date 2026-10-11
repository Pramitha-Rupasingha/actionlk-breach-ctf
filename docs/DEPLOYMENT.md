# Deployment Guide

This turns the Assignment 01 design report into a running box. It follows
the same order as the architecture diagram: **Host (Docker) → CTFd control
layer → isolated network → challenge containers → participant machine
(Kali)**.

```
actionlk-breach-ctf/
├── docker-compose.yml          ← the whole stack, one command to run it
├── .env.example                ← docker-compose variables (copy to .env)
├── secrets.env.example         ← every flag/credential (copy to secrets.env)
├── scripts/generate_assets.py  ← (re)builds profile.jpg / pcap / vault.enc
├── scripts/apply_theme.sh      ← applies the CTFd branding through its API
├── branding/                   ← logo, favicon, terminal-style CSS for CTFd
├── stage3-frontdoor/           ← live container
├── stage5-behindthedoor/       ← live container
└── static-challenges/          ← files to attach directly in CTFd
```

Stages 1, 2, 4, 6 are static files uploaded straight into CTFd (no
container needed). Stages 3 and 5 are the two live Docker services, exactly
as drawn in Figure 1 of the report.

---

## Part A — Host machine (Ubuntu Server 22.04 LTS)

Do this on the Ubuntu Server VM (under UTM), not on your Mac or on Kali.

### 1. Install Docker Engine + Compose plugin

```bash
sudo apt update && sudo apt install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo usermod -aG docker $USER   # log out/in once so `docker` works without sudo
```

### 2. Get the project onto the VM

```bash
sudo apt install -y git
git clone git@github.com:<owner>/actionlk-breach-ctf.git
cd actionlk-breach-ctf
```

(No GitHub access on the VM? `scp -r` the folder over instead.)

### 3. Create your env files, set the VM's IP, generate the assets

```bash
cp .env.example .env
cp secrets.env.example secrets.env
```

Edit both files (change every `CHANGE_ME_*` value, keep the shared values
identical in both). `.env` and `secrets.env` are git-ignored, so your real
flags never reach GitHub.

Find the VM's LAN/bridge IP (the one Kali will use to reach it):

```bash
ip -4 addr show | grep inet
```

Put that IP in **both** `secrets.env` and `.env` as `PASV_ADDRESS`
(needed for FTP passive mode in Stage 5 — without this, FTP data transfers
will hang from outside the container).

If this is your first time generating assets, or you changed any value in
`secrets.env` (flags, surname, FTP password, Caesar shift):

```bash
pip3 install --break-system-packages pillow   # only needed once
python3 scripts/generate_assets.py
```

This (re)writes `profile.jpg`, `encoded_note.txt`, `capture.pcap` and
`vault_backup.zip.enc` so every stage stays consistent with `secrets.env`.
**If you change a flag, always re-run this script before rebuilding.**

### 4. Lock down internet egress from the challenge network

`docker-compose.yml` disables container-to-container traffic on the
challenge network (`enable_icc: false`), but a normal bridge network still
lets containers reach the internet by default. Add one rule on the host to
block that, while still allowing the published ports players use:

```bash
sudo iptables -I DOCKER-USER -s 172.20.0.0/24 -m conntrack --ctstate NEW -j DROP
```

This blocks *new* outbound connections starting from inside Stage 3 /
Stage 5, but doesn't touch the established connections players' own
requests create — so the challenges stay reachable. Make it persist across
reboots with `sudo apt install -y iptables-persistent` and saving the rule.

### 5. Build and start everything

```bash
docker compose up -d --build
docker compose ps        # all five services should show "Up"
docker compose logs -f stage3-frontdoor   # ctrl-C once you see "Starting Apache"
```

CTFd is now on `http://<ubuntu-vm-ip>:8000`, Stage 3 on `:8003`, Stage 5's
web portal on `:8005`, and Stage 5's FTP on port `21`.

### 6. Finish CTFd setup

Open `http://<ubuntu-vm-ip>:8000` in a browser, run the CTFd setup wizard
(event name **ActionLK Breach**, create your admin account), then in
**Admin Panel → Config**:
- Turn on **rate limiting** for flag submissions (Config → General).
- Set submission log visibility to admin-only (default).

Then **Admin Panel → Challenges → Create** once per stage:

| Stage | Category | Description source | Flag | Attachment / connection info |
|---|---|---|---|---|
| 1 | OSINT | `static-challenges/stage1-public-trail/description.md` | in `secrets.env` (`STAGE1_FLAG`) | attach `profile.jpg` |
| 2 | Cryptography | `.../stage2-encoded-note/description.md` (paste in the encoded string) | `STAGE2_FLAG` | none (text only) |
| 3 | Web Security | write from the report's Stage 3 spec | `STAGE3_FLAG` | `http://<ubuntu-vm-ip>:8003` |
| 4 | Networking | `.../stage4-sniffing-the-wire/description.md` | `STAGE4_FLAG` | attach `capture.pcap` |
| 5 | Web + Networking | write from the report's Stage 5 spec | `STAGE5_PARTIAL_FLAG` | FTP `<ubuntu-vm-ip>:21`, web `http://<ubuntu-vm-ip>:8005` |
| 6 | Cryptography | `.../stage6-the-vault/description.md` | `STAGE6_FLAG` | attach `vault_backup.zip.enc` |

Use **exact match** flags (CTFd's default "static" flag type) for all six,
matching the report's validation method.

---

## Part B — Attacker machine (Kali)

Run Kali as its own VM (UTM, same **Bridged/Shared** network as the Ubuntu
Server VM so both get LAN IPs that can reach each other) or as a live
USB/laptop on the same network.

### 1. Confirm connectivity

```bash
ping <ubuntu-vm-ip>
curl -I http://<ubuntu-vm-ip>:8000
```

### 2. Tools (Kali ships with most of these; a couple need installing)

```bash
sudo apt update
sudo apt install -y exiftool wireshark ftp
```

Burp Suite Community is preinstalled under **Applications → 03 - Web
Application Analysis**. CyberChef doesn't need installing — open
`https://gchq.github.io/CyberChef/` in the Kali browser, or download the
single-file offline build if the box needs to run fully air-gapped from
the real internet.

### 3. Point the browser at Burp

Firefox (Kali's default) → Settings → Network Settings → Manual proxy →
`127.0.0.1:8080` for HTTP/HTTPS. In Burp: **Proxy → Intercept** to toggle
capturing, **Proxy → HTTP history** to review past requests, and send any
request to **Repeater** with `Ctrl+R` to replay/edit it — this is what
Stages 3 and 5 are built around.

---

## Reset / recovery

Matches the report's "Reset / Recovery" field for each live stage:

```bash
docker compose restart stage3-frontdoor      # wipes back to seeded DB state
docker compose restart stage5-behindthedoor  # re-renders vsftpd + Flask
```

Static stages (1, 2, 4, 6) never need a reset — they're just files.

## Isolation check (from the report's Testing/Validation Plan)

From inside a challenge container, confirm it can't reach the other
container or the internet:

```bash
docker compose exec stage3-frontdoor bash -c "apt-get install -y iputils-ping >/dev/null 2>&1; ping -c1 -W2 8.8.8.8 || echo 'no internet egress, as designed'"
docker compose exec stage3-frontdoor bash -c "ping -c1 -W2 <stage5 container IP> || echo 'no inter-container access, as designed'"
```

Both pings should fail — that failure is the isolation working correctly.

## Changing flags / secrets later

Edit `secrets.env`, mirror the FTP/DB values into `.env`, re-run
`python3 scripts/generate_assets.py`, then:

```bash
docker compose up -d --build
```

Update the flags stored in CTFd's admin panel to match — CTFd doesn't read
`secrets.env` itself, it only validates whatever flag string you typed in
when creating each challenge.

## Branding the CTFd UI (optional)

The logo, favicon and terminal-style CSS live in `branding/`. After CTFd
setup, create an admin access token (CTFd → Settings → Access Tokens) and run:

```bash
CTFD_TOKEN=ctfd_xxxxxxxx bash scripts/apply_theme.sh
```

Prefer clicking? Paste `branding/theme-header.html` into
**Admin Panel → Config → Theme → Theme Header**, and upload the two SVGs as
Logo / Small Icon.
