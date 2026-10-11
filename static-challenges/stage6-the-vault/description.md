# STAGE-06 — The Vault (Capstone)

**Category:** Cryptography · **Difficulty:** Hard

The encrypted vault backup recovered in Stage 5 holds the final proof of
how the breach occurred — proof that only makes sense once combined with
two earlier fragments of the investigation.

**Passphrase rule:** `<employee surname from Stage 1>_<decoded word from
Stage 2>`, all lowercase, one underscore, no spaces.

Decrypt with:
```
openssl enc -d -aes-256-cbc -pbkdf2 -in vault_backup.zip.enc -out vault_backup.zip -k <passphrase>
unzip vault_backup.zip
```

**Attach in CTFd:** `vault_backup.zip.enc`
**Flag format:** `ACTIONLK{...}` — found inside the decrypted archive.

**Hints (suggested point deductions):**
- (-10) Look back at the employee's name and the decoded word — combine them.
- (-20) Format: `surname_word`, all lowercase, one underscore.
