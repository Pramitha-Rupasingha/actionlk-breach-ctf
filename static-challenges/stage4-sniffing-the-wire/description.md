# STAGE-04 — Sniffing the Wire

**Category:** Networking · **Difficulty:** Moderate

The admin dashboard from Stage 3 references an internal file server
reached over FTP. A packet capture spanning that period has been
recovered. Open it and find out what the attacker saw.

**Attach in CTFd:** `capture.pcap`
**Flag format:** `ACTIONLK{...}` — the extracted password, wrapped in the
standard flag format.

**Hints (suggested point deductions):**
- (-5) Filter by protocol — `ftp`.
- (-10) FTP doesn't encrypt anything. Follow the TCP stream.
