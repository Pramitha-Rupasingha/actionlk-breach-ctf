# Organiser Walkthrough (SPOILERS)

> **Contains full solutions for every stage.** For organisers and markers
> only. If the repository is ever made public, delete this file first.

This is the end-to-end play-through used to validate the box against the
design report's testing plan. Run it from the Kali machine.

## Play through it once, end to end

1. Open `http://<ubuntu-vm-ip>:8000`, register/log in, open **Stage 1**,
   download `profile.jpg`, run `exiftool profile.jpg` → read the Comment
   field → submit the flag.
2. **Stage 2**: copy the encoded string from the challenge description into
   CyberChef → `From Base64` → `ROT13 Brute Force` (or manual `ROT47`/Caesar
   recipe) until it reads `ACTIONLK{...}` → submit.
3. **Stage 3**: browse to `http://<ubuntu-vm-ip>:8003` with Burp
   intercepting. Submit the login form once, send the captured POST to
   Repeater, change the `username` field to `admin'-- -` (leave password as
   anything — the `-- ` comments out the password check), resend, confirm
   the response now logs you in as `admin` specifically, then load
   `dashboard.php` in-browser and submit the flag.
4. **Stage 4**: download `capture.pcap`, open in Wireshark, filter `ftp`,
   right-click a packet → **Follow → TCP Stream**, read the `PASS` line,
   submit `ACTIONLK{<that password>}`.
5. **Stage 5**: `ftp <ubuntu-vm-ip>`, log in with the Stage 4 credentials,
   `get hint.txt`, read it. Then browse
   `http://<ubuntu-vm-ip>:8005/files?user_id=1042` with Burp running, send
   the GET to Repeater, change `user_id` to `1000`, resend, download
   `admin_notes.txt` and `vault_backup.zip.enc` from the listing, submit the
   partial flag from `admin_notes.txt`.
6. **Stage 6**: `openssl enc -d -aes-256-cbc -pbkdf2 -in vault_backup.zip.enc
   -out vault_backup.zip -k perera_midnight` (surname from Stage 1 + word
   from Stage 2, lowercase, one underscore) → `unzip vault_backup.zip` →
   read the flag inside → submit.

If every stage above lands, the box matches the design report end to end.
