# Contributing

Four people work on this repo. To keep history clean and give everyone proper
credit on GitHub, **each member commits and pushes their own part** from their
own account, on their own branch, and merges through a Pull Request.

## Who owns what

| Member | Branch name | Paths they push |
|--------|-------------|-----------------|
| Rupasingha R.S.M.P.S. (1) | `platform-rupasingha` | `docker-compose.yml`, `docs/DEPLOYMENT.md` |
| Venura Kithpura W.K. (2) | `stage1-3-venura` | `static-challenges/stage1-public-trail/`, `static-challenges/stage2-encoded-note/`, `stage3-frontdoor/`, `branding/`, `scripts/apply_theme.sh` |
| Bandara L.M.I.L. (3) | `stage4-6-bandara` | `static-challenges/stage4-sniffing-the-wire/`, `static-challenges/stage6-the-vault/`, `stage5-behindthedoor/` |
| Wickramasinghe A.H. (4) | `docs-testing-wickramasinghe` | `docs/WALKTHROUGH.md`, `scripts/generate_assets.py`, later edits to `README.md` and `CONTRIBUTING.md` |

The first commit on `main` (README, `.gitignore`, the two `*.example` env files)
is pushed by whoever creates the repository so everyone has a base to branch from.
Only edit files you own. If you need a change in someone else's file, ask them
or open an issue.

## One-time setup (each member, on their own machine)

```bash
sudo apt install -y git                       # Ubuntu; on macOS git comes with Xcode tools
git config --global user.name  "Your Name"
git config --global user.email "the-email-on-your-github-account"

# SSH key so you can push (GitHub no longer accepts account passwords for git)
ssh-keygen -t ed25519 -C "the-email-on-your-github-account"
cat ~/.ssh/id_ed25519.pub     # paste into GitHub -> Settings -> SSH and GPG keys
ssh -T git@github.com         # should greet you by username
```

The email must match one on your GitHub account (or your
`<id>+<username>@users.noreply.github.com` address), otherwise your commits will
not be linked to your profile.

## Workflow for every change

```bash
git clone git@github.com:<owner>/actionlk-breach-ctf.git     # first time only
cd actionlk-breach-ctf

git switch main && git pull                  # start from the latest main
git switch -c <your-branch-name>             # see the table above

# copy / edit ONLY the paths you own, then:
git status                                   # .env and secrets.env must NOT be listed
git add <your paths>
git commit -m "feat(stage3): add front door login portal"
git push -u origin <your-branch-name>
```

Then open GitHub, click **Compare & pull request**, and ask a teammate to
review. After it is merged, update your copy with `git switch main && git pull`.

### Commit messages

`type(scope): short summary`, where type is `feat`, `fix`, `docs` or `chore`.
Examples: `feat(stage5): add IDOR file portal`, `docs: add isolation test results`.

## Rules

1. **Never commit `.env` or `secrets.env`.** They are in `.gitignore`; keep it that way.
   Share real values with the team privately, not through Git.
2. Do not edit files owned by someone else without telling them.
3. Never commit directly to `main` after the first skeleton commit; use a branch and a PR.
4. If you change a flag or credential, update `secrets.env.example` / `.env.example`
   (placeholders only) and re-run `python3 scripts/generate_assets.py`.
