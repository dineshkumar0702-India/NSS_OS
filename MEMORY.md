# OpenNAS-Lite (NSS_OS) — project memory (start → now)

**Purpose:** After a Windows reboot (or new Cursor chat), open this file and tell the agent:  
**“Read `MEMORY.md` and continue where we left off.”**

**Last updated:** 2026-10-10 (local)  
**Workspace:** `C:\Cursor_Projets\NSS_OS`  
**Product codename:** OpenNAS-Lite (UGOS-like open NAS on Debian 12, amd64, old hardware)

---

## 1. User goals (your intent)

1. Build a **bootable ISO** and test in **VMware Workstation**, then on **older physical hardware**.
2. Avoid **Windows reboot** for WSL if possible — use **GitHub Actions** to build the ISO.
3. **English-only** web UI (Hindi removed earlier).
4. Phased delivery per `MASTER_PROMPT.md` — **Phases 1–7 are implemented in the repo**; **ISO not successfully built in CI yet**.

---

## 2. GitHub & local git

| Item | Value |
|------|--------|
| Profile | https://github.com/dineshkumar0702-India |
| Repo | https://github.com/dineshkumar0702-India/NSS_OS (public) |
| Remote | `origin` → `https://github.com/dineshkumar0702-India/NSS_OS.git` |
| Branch | `main` |
| Workflow | `.github/workflows/build-iso.yml` — **Build OpenNAS-Lite ISO** |

**After reboot — sync:**

```powershell
cd C:\Cursor_Projets\NSS_OS
git pull origin main
```

**Push local commits (if any):**

```powershell
git push origin main
```

**GitHub CLI** installed at `C:\Program Files\GitHub CLI\gh.exe` — run `gh auth login` once if you want CLI access (agent cannot use your login).

**Node.js** installed (v24.x) — `C:\Program Files\nodejs\` (npm/npx for local web builds).

---

## 3. CI status (as of last session)

| Commit | lint-openapi | build-iso | Notes |
|--------|--------------|-----------|--------|
| `a394193` / earlier | fail | skip | OpenAPI Redocly errors |
| `5d4a8b0` | **pass** | **fail** | npm ERESOLVE (Svelte 4 vs vite-plugin-svelte 4) |
| `43872d6` | **pass** | **fail** | npm/web fixed; **live-build** stage failed (get log from Actions) |

**Actions URL:** https://github.com/dineshkumar0702-India/NSS_OS/actions  

**When build-iso fails:** open the failed run → **build-iso** job → copy log to `ErrorLogs\` and ask agent to fix.

**When build-iso succeeds:** download artifact **opennas-lite-iso** → extract `opennas-lite-bookworm-amd64.iso` to `build\output\`.

---

## 4. CI fixes already applied (do not redo blindly)

### OpenAPI / lint-openapi

- `openapi/openapi.yaml`: `security: []` on `/auth/login`; `confirm_token` as optional `string` (not `nullable` / not `type: [string, null]`).
- `redocly.yaml` + pinned `@redocly/cli@1.34.4` in `build/scripts/lint-openapi.sh`.
- `.gitattributes` (LF), CRLF strip step in workflow.

### Web UI / prepare-iso-assets

- `src/web/package.json`: `@sveltejs/vite-plugin-svelte@^3.1.2`, `@sveltejs/kit` ~2.16.
- `src/web/svelte.config.js`: `vitePreprocess()` for TypeScript in Svelte.
- `src/web/package-lock.json` committed.
- `build/scripts/prepare-iso-assets.sh`: on web build failure → **fallback** static page under `build/assets/web-fallback/`.

---

## 5. What the product is (phases 1–7)

| Phase | Deliverable |
|-------|-------------|
| 1 | `docs/architecture/*`, assumptions, OpenAPI stub |
| 2 | `build/live-build/`, Calamares, `build/scripts/build-iso.sh` |
| 3 | `src/daemon/` (`nasd`, `nasctl`), tests in `tests/` |
| 4 | `src/web/` SvelteKit static UI |
| 5 | Apps, backups, snapshots, VPN, notifications, VM stub |
| 6 | OTA, security advisor, diagnostics, `docs/TESTING.md` |
| 7 | `docs/INSTALL.md`, `ADMIN.md`, `DEVELOPER.md`, `HARDWARE.md`, `ROADMAP.md` |

**Spec:** `MASTER_PROMPT.md`  
**Summaries:** `docs/PHASE1-SUMMARY.md` … `docs/PHASE7-SUMMARY.md`

---

## 6. ISO contents (intended)

Staged by `build/scripts/prepare-iso-assets.sh` + `stage-includes.sh` + hook `0400-opennas-nasd.hook.chroot`:

- Calamares + OpenNAS profile/partition modules
- `nasd` installed via pip from staged `src/daemon`
- Caddy + systemd `nasd.service`
- Web UI → `/usr/share/opennas/web` (or fallback HTML)
- App templates → `/usr/share/opennas/apps`

**Output path (after successful build):**  
`build/output/opennas-lite-bookworm-amd64.iso`

---

## 7. Safety flags (appliance defaults)

| Env var | Default | Meaning |
|---------|---------|---------|
| `NASD_ALLOW_STORAGE_MUTATIONS` | `false` | Real disk/pool ops simulated |
| `NASD_ALLOW_DOCKER_OPS` | `false` | Docker app lifecycle simulated |
| `NASD_ALLOW_SYSTEM_UPGRADE` | `false` | OTA/apt simulated |

Enable only on **throwaway VMs** — see `docs/VMWARE.md` and `docs/ADMIN.md`.

---

## 8. How to build the ISO (paths)

### A. GitHub Actions (preferred on Windows, no reboot)

See `docs/GITHUB-ISO-BUILD.md`.

### B. WSL (needs reboot first time)

`.\build\scripts\Build-Iso-Wsl.ps1`

### C. Debian builder VM in VMware (no Windows reboot)

`docs/BUILD-NO-REBOOT.md` + `build/scripts/debian-guest-build.sh`

### D. Docker

`build/scripts/build-iso-docker.sh`

---

## 9. VMware testing (after ISO exists)

`docs/VMWARE.md` — sample VMX: `build/vmware/opennas-lite-test.vmx`  
Typical lab VM: 2 vCPU, 2–4 GB RAM, 32 GB disk, UEFI, attach ISO.

---

## 10. Key paths

```
NSS_OS/
├── MEMORY.md                 ← this file
├── MASTER_PROMPT.md
├── README.md
├── src/daemon/nasd/          # FastAPI nasd
├── src/web/                  # SvelteKit UI
├── build/scripts/build-iso.sh
├── build/live-build/         # debian live-build
├── openapi/openapi.yaml
├── tests/                    # pytest (13 tests)
├── ErrorLogs/                # paste GitHub failure logs here
└── docs/GITHUB-ISO-BUILD.md
```

**Tests (local):**

```powershell
cd C:\Cursor_Projets\NSS_OS\src\daemon
python -m pytest ../../tests -q
```

**Web build (local):**

```powershell
cd C:\Cursor_Projets\NSS_OS\src\web
npm ci
npm run build
```

---

## 11. Immediate next work (after reboot)

1. **Pull** latest `main`; confirm latest Actions run on GitHub.
2. **Fix `build-iso` failure** on commit `43872d6` (or newer):
   - Download **build-iso** job log from Actions OR save to `ErrorLogs\<commit>logs.txt`.
   - Agent should read log and fix `live-build` / hooks / package lists / permissions (common: `lb build`, hook errors, missing packages, `pip install` in chroot).
3. When ISO artifact is green, **download ISO** → VMware install per `docs/VMWARE.md`.
4. Optional: make repo **private** if you prefer (currently public).
5. Optional: `gh auth login` for easier log/PR access from terminal.

---

## 12. Conversation / context notes

- User on **Windows 10/11**; **WSL was not installed** (reboot avoided).
- Agent **cannot log into GitHub** as the user; it can read **public** repo metadata via API.
- `chat.txt` in repo root is a **local export** — **gitignored** (`chat.txt` in `.gitignore`).
- Cursor chat transcripts may persist under Cursor’s project data; **`MEMORY.md` is the canonical handoff** for the codebase.

---

## 13. One-line prompt for the next session

Copy-paste into Cursor:

> Read `C:\Cursor_Projets\NSS_OS\MEMORY.md`. The GitHub Actions **build-iso** job is still failing after lint passed (latest push `43872d6`). I will paste the build-iso log in `ErrorLogs` if needed. Fix the ISO build, push to `main`, and tell me when the artifact is ready for VMware.

---

*End of memory file.*
