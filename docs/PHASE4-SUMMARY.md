# Phase 4 summary — Web UI

## What was done

1. **SvelteKit app** — `src/web/` with `@sveltejs/adapter-static`, SPA fallback `index.html`.
2. **Pages** — Setup, login, dashboard, storage (pool dry-run/confirm), shares, users, files browser, apps placeholder.
3. **Copy** — English UI strings in `src/lib/i18n.ts` (Hindi removed in Phase 5).
4. **Themes** — Light/dark via CSS variables (`data-theme` on `<html>`).
5. **API client** — Cookie-based session (`credentials: 'include'`), Vite dev proxy to `nasd`.
6. **Backend** — `GET /api/v1/files` for read-only directory listing under allowed roots.
7. **Build script** — `build/scripts/build-web.sh` → `build/output/web/`.

## How to test

```bash
# Terminal 1
cd src/daemon && pip install -e .
export NASD_DATA_DIR=/tmp/nasd NASD_COOKIE_SECURE=false
nasd --host 127.0.0.1 --port 8741

# Terminal 2
cd src/web && npm install && npm run dev
```

1. Open `http://localhost:5173` → complete setup → login.
2. Exercise dashboard, storage dry-run, users, shares (needs volume UUID).
3. Files page lists `/data` if the path exists on the host (may be empty on Windows).

Production build:

```bash
bash build/scripts/build-web.sh
```

## What comes next (Phase 5 — wait for `continue`)

Backup, snapshots, App Center, VM, VPN, notifications, photos/media modules.

Reply **`continue`** for Phase 5.
