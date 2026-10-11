# Risks, Dependencies & Limitations

Source: Assignment 01 design report, *Risks, Dependencies & Limitations*. Owner: Member 4 (Wickramasinghe A.H.).

## Risks and mitigations

| Risk | Mitigation and status |
|---|---|
| A compromised challenge container could reach another challenge container or the internet. | Stage 3 and Stage 5 use the `ctf_isolated` bridge with inter-container communication disabled. The project also uses a host firewall rule to block outbound connections. Testing recorded Stage 3 internet access and cross-stage access as blocked on 2026-10-11. Stage 5 outbound internet access should also be checked before claiming that both challenge containers are blocked. |
| Players could guess flags repeatedly. | Configure per-challenge attempt limits in CTFd and review submission activity. Confirm these controls are enabled before describing them as implemented. |
| The Stage 6 passphrase could be ambiguous or impossible to derive. | Use the defined rule: the lowercase Stage 1 employee surname, an underscore, then the decoded Stage 2 word. The passphrase was tested; see the results and evidence in [TESTING.md](TESTING.md). |
| A broken stage could make later stages unsolvable. | Run fresh-eyes tests and a complete Stage 1–6 walkthrough before release. The testing record reports that all six stages were solved with no problems found; see [TESTING.md](TESTING.md). |

## Dependencies

- Stage 3 points players toward the FTP evidence used in Stage 4. Stage 4’s recovered FTP credentials are needed for the Stage 5 path.
- Stage 5 provides the encrypted vault used in Stage 6.
- Stage 6’s passphrase depends on the employee surname found in Stage 1 and the decoded word found in Stage 2.
- Because later stages rely on earlier clues and files, a broken or changed earlier-stage artifact can block progress. Re-run the end-to-end walkthrough after changing a stage or its generated assets.

## Limitations

- CTFd is exposed over HTTP on port 8000; the supplied Compose setup does not include HTTPS or a TLS reverse proxy.
- Docker Compose publishes the challenge services directly: Stage 3 on port 8003, Stage 5 web on port 8005, and FTP on port 21 with passive ports 21100–21110. Keep these ports restricted to the authorized lab network.
- The network configuration disables inter-container communication, but internet egress also depends on the host firewall rule. The test record checks Stage 3 egress; Stage 5 egress still needs confirmation.
- Restarting a container is not a complete reset. Stage 3 may need to be force-recreated to restore its database. Stage 5 recreates some FTP configuration on startup but does not restore every changed file. The current reset checks did not begin with deliberately modified state, so restoration from a modified state is not yet demonstrated.
- Stage 5 uses a file portal and an in-memory user-to-file mapping rather than a database. Its state and behavior are specific to the running container.
- Stages 1, 2, 4, and 6 use static challenge artifacts attached to CTFd, so those files and their configured flags must remain consistent.

## Differences between the design report and the implementation

| Design report | Actual implementation and verification | Explanation or outstanding action |
|---|---|---|
| Only the CTFd host publishes ports to players. | Compose publishes CTFd on port 8000, Stage 3 on port 8003, Stage 5 web on port 8005, and FTP on port 21 with passive ports 21100–21110. The testing record reports that Kali could reach the required challenge ports. | Restrict published ports to the authorized lab network and document the actual ports. |
| Challenge containers have no internet access and cannot communicate with other containers. | The challenge bridge sets `enable_icc: "false"` but does not set `internal: true`. Outbound blocking depends on a separate host firewall rule. The testing record reports Stage 3 internet access and cross-stage access as blocked. | Also test Stage 5 outbound internet access before claiming that egress is blocked from both challenge containers. |
| Players access the platform over HTTPS. | CTFd is published over HTTP on port 8000. The supplied Compose file has no TLS reverse proxy. | HTTPS is not implemented in this deployment. Treat the playbox as a lab system and do not present the HTTP setup as production-ready. |
| Reset instructions use `web-portal`, `file-share`, and `webapp2`. | The actual challenge service names are `stage3-frontdoor` and `stage5-behindthedoor`. | Use the actual names in setup and testing commands. |
| Restarting the challenge services restores their initial state. | Recreating Stage 3 can restore its container’s seeded database. Stage 5 refreshes FTP credentials, the hint file, and configuration on startup, but does not restore every application file. | A restart is not a complete reset guarantee. Test recovery after deliberately changing state and document the verified reset procedure. The current tests did not record a pre-restart change. |
| Flags follow `ACTIONLK{lowercase_words_and_numbers}`. | The Stage 4 flag contains uppercase characters and a symbol inside the `ACTIONLK{...}` wrapper. | The flag format must permit the characters used by the Stage 4 flag. The testing record reports exact-match checks for all six stages in [TESTING.md](TESTING.md). |
| Stage 5 uses Python 3.11 with MySQL, and CTFd uses PostgreSQL or SQLite. | Stage 5 uses Python 3.11, Flask 3.0.3, and vsftpd. Its file portal uses files and an in-memory user-to-file mapping, not a database. CTFd uses MariaDB 10.11 and Redis 7. | Keep the architecture description and diagram aligned with these components. |