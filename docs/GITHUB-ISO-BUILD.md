# Build the ISO with GitHub Actions

No WSL and no Windows reboot. GitHub compiles the ISO; you download it as an artifact.

## 1. One-time: create an empty GitHub repository

1. Sign in at [github.com](https://github.com).
2. **New repository** → name e.g. `NSS_OS` or `opennas-lite`.
3. **Private** recommended.
4. Do **not** add README, .gitignore, or license (this repo already has them).
5. Copy the HTTPS URL. For this project, use repo name **`NSS_OS`**:

   `https://github.com/dineshkumar0702-India/NSS_OS.git`

   Profile: [github.com/dineshkumar0702-India](https://github.com/dineshkumar0702-India)

## 2. Push from this PC (PowerShell)

```powershell
cd C:\Cursor_Projets\NSS_OS

# If you already committed locally, only add remote + push:
git branch -M main
git remote add origin https://github.com/dineshkumar0702-India/NSS_OS.git
git push -u origin main
```

**Or with GitHub CLI** (after `gh auth login` in a normal terminal):

```powershell
gh repo create dineshkumar0702-India/NSS_OS --private --source=. --remote=origin --push
```

GitHub will ask you to sign in on push. Use a **Personal Access Token** as the password if prompted ([create token](https://github.com/settings/tokens) with `repo` scope).

## 3. Run the ISO workflow

1. On GitHub: **Actions** → **Build OpenNAS-Lite ISO**.
2. If this is the first push, the workflow may start automatically on `push`.
3. Otherwise: **Run workflow** → branch `main` → **Run workflow**.
4. Wait ~30–90 minutes (job **build-iso**).
5. Open the completed run → **Artifacts** → download **opennas-lite-iso**.
6. Extract `opennas-lite-bookworm-amd64.iso` to:

   `C:\Cursor_Projets\NSS_OS\build\output\`

## 4. Test in VMware

[VMWARE.md](VMWARE.md) — attach the ISO to a new VM and install.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `lint-openapi` fails | Fix `openapi/openapi.yaml` or open a PR; check Actions log |
| `build-iso` needs approval | Repo **Settings** → **Actions** → allow workflows for private repos |
| Push rejected | `git pull --rebase origin main` then push again |
| No artifact | Open **build-iso** job log; see `build/logs/live-build.log` in the log output |

## Keep working locally

```powershell
git add -A
git commit -m "Describe your change"
git push
```

Each push can rebuild the ISO if the workflow is enabled on push.
