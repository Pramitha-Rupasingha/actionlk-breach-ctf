# Testing & Validation Plan

Source: Assignment 01 design report, *Testing / Validation Plan*. Owner: Member 4 (Wickramasinghe A.H.). This file records test results, testers, dates, and evidence.

> The full end-to-end walkthrough is in [WALKTHROUGH.md](WALKTHROUGH.md) for organisers. The commands below use the service names from `docker-compose.yml`: `stage3-frontdoor` and `stage5-behindthedoor`.

## 1. Fresh-eyes testing

Each stage was solved end-to-end by a team member who did not design it.

| Stage | Designed by | Tested by | Result | Date | Evidence |
|---|---|---|---|---|---|
| 1: The Public Trail | Venura | Asirindu | Pass | 2026-10-08 | [View screenshot](evidence/stage1-flag-accepted.png) |
| 2: The Encoded Note | Venura | Asirindu | Pass | 2026-10-09 | [View screenshot](evidence/stage2-flag-accepted.png) |
| 3: Front Door | Venura | Asirindu | Pass | 2026-10-09 | [View screenshot](evidence/stage3_06_ctfd_accepted.png) |
| 4: Sniffing the Wire | Bandara | Asirindu | Pass | 2026-10-09 | [View screenshot](evidence/stage4_03_ctfd_accepted.png) |
| 5: Behind the Door | Bandara | Asirindu | Pass | 2026-10-09 | [View screenshot](evidence/stage5_05_ctfd_accepted.png) |
| 6: The Vault | Bandara | Asirindu | Pass | 2026-10-10 | [View screenshot](evidence/stage6_04_ctfd_accepted.png) |

## 2. Stage 6 passphrase test

The Stage 6 passphrase follows this rule: the lowercase employee surname from Stage 1, an underscore, then the decoded word from Stage 2.

Run these commands on the machine where `vault_backup.zip.enc` was downloaded. If it is in `~/Downloads`, use:

```bash
cd ~/Downloads
openssl enc -d -aes-256-cbc -pbkdf2 \
  -in vault_backup.zip.enc \
  -out vault_backup.zip \
  -k "perera_midnight"

unzip vault_backup.zip
cat incident_report_final.txt
```

| Check | Expected | Result | Date | Evidence |
|---|---|---|---|---|
| Decrypt with the derived passphrase | Archive extracts and the final flag file is readable | Pass | 2026-10-10 | [Successful decryption](evidence/stage6_02_flag_file.png) |
| Decrypt with a wrong passphrase | Decryption fails with a `bad decrypt` error | Pass | 2026-10-10 | [Wrong passphrase failure](evidence/stage6_03_wrong_passphrase_fail.png) |

## 3. Flag exact-match check

For each stage, submit the correct flag and a near-miss through the CTFd challenge submission form or preview. Confirm that the correct flag is accepted and the near-miss is rejected.

| Stage | Correct flag accepted | Near-miss rejected | Date |
|---|---|---|---|
| 1 | Yes | Yes | 2026-10-09 |
| 2 | Yes | Yes | 2026-10-09 |
| 3 | Yes | Yes | 2026-10-10 |
| 4 | Yes | Yes | 2026-10-10 |
| 5 | Yes | Yes | 2026-10-10 |
| 6 | Yes | Yes | 2026-10-11 |

## 4. Container restart and recreation checks

Run these commands from the project folder. Stage 3 is force-recreated so its container starts with the seeded database. Stage 5 is restarted so its startup configuration runs again.

```bash
sudo docker compose up -d --force-recreate stage3-frontdoor
sudo docker compose restart stage5-behindthedoor
```

After each command, check that the relevant stage loads. No state was deliberately changed before these checks, so they confirm that the services start again; they do not prove recovery from deliberately modified data.

| Stage | State changed before test | Result after restart/recreation | Date |
|---|---|---|---|
| 3 | No changes made before recreation | Stage loaded after container recreation | 2026-10-11 |
| 5 | No changes made before restart | Portal loaded after restart | 2026-10-11 |

## 5. Isolation checks

The following tests use Bash’s built-in `/dev/tcp` feature and do not require extra packages. Run them from the project folder in Ubuntu.

```bash
# Positive control: Stage 3 can reach itself (expect: OK)
sudo docker compose exec stage3-frontdoor \
  bash -c 'timeout 3 bash -c "</dev/tcp/127.0.0.1/80" && echo OK || echo FAIL'

# Stage 3 internet egress (expect: blocked)
sudo docker compose exec stage3-frontdoor \
  bash -c 'timeout 3 bash -c "</dev/tcp/8.8.8.8/53" && echo REACHABLE || echo blocked'

# Stage 3 to Stage 5 (expect: blocked)
S5_IP=$(sudo docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' \
  "$(sudo docker compose ps -q stage5-behindthedoor)")
sudo docker compose exec stage3-frontdoor \
  bash -c "timeout 3 bash -c '</dev/tcp/${S5_IP}/80' && echo REACHABLE || echo blocked"

# Stage 5 to Stage 3 (expect: blocked)
S3_IP=$(sudo docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' \
  "$(sudo docker compose ps -q stage3-frontdoor)")
sudo docker compose exec stage5-behindthedoor \
  bash -c "timeout 3 bash -c '</dev/tcp/${S3_IP}/80' && echo REACHABLE || echo blocked"

# Stage 5 internet egress (expect: blocked)
sudo docker compose exec stage5-behindthedoor \
  bash -c 'timeout 3 bash -c "</dev/tcp/8.8.8.8/53" && echo REACHABLE || echo blocked'
```

From Kali, check that players can still reach the published services. Replace `<Ubuntu-IP>` with the Ubuntu VM’s current IP address:

```bash
nc -vz <Ubuntu-IP> 8003
nc -vz <Ubuntu-IP> 8005
nc -vz <Ubuntu-IP> 21
```

| Check | Expected | Result | Date |
|---|---|---|---|
| Stage 3 to itself (positive control) | OK | OK | 2026-10-11 |
| Stage 3 to internet | blocked | blocked | 2026-10-09 |
| Stage 5 to internet | blocked | blocked | 2026-10-11 |
| Stage 3 to Stage 5 | blocked | blocked | 2026-10-11 |
| Stage 5 to Stage 3 | blocked | blocked | 2026-10-11 |
| Kali can reach ports 8003, 8005, and FTP 21 | reachable | reachable | 2026-10-11 |

The Compose network disables inter-container communication. Blocking outbound internet access also depends on the host firewall rule described in the project setup instructions.

## 6. Full path walkthrough

Stage 1 through Stage 6 were solved in order from the Kali machine, following [WALKTHROUGH.md](WALKTHROUGH.md), to check that the stages and dependencies worked together.

| Run | Tester | Stages solved | Problems found | Date |
|---|---|---|---|---|
| 1 | Asirindu | Stages 1–6 | None | 2026-10-10 |
