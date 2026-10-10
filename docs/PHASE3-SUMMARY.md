# Phase 3 summary — Core daemon and CLI

## What was done

1. **`nasd`** — FastAPI app under `src/daemon/nasd/` with SQLite models matching the Phase 1 data model (core tables).
2. **API routes** — Auth, system setup/status/capabilities, storage (disks, pools dry-run/confirm/jobs), users, shares (+ Samba render), network interfaces, services status, firewall, jobs.
3. **Safety** — Pool create requires `dry_run` + `confirm_token`; mutations to disks default **off** (`NASD_ALLOW_STORAGE_MUTATIONS=false`, jobs simulate).
4. **`nasctl`** — Entry point with `status`, `capabilities`, `login`, `disks` (`src/daemon/nasd/cli.py`).
5. **Config renderers** — Samba `smb.conf`, default nftables ruleset.
6. **Seed loader** — Imports `config.seed.json` / install profile on first DB init.
7. **Tests** — `tests/test_api.py` with pytest + TestClient.
8. **systemd** — `packaging/systemd/nasd.service`, optional `nasd.socket`, Caddy snippet `packaging/caddy/opennas.caddy`.

## How to test

```bash
cd src/daemon
pip install -e ".[dev]"
pytest ../../tests -q
```

Manual smoke:

```bash
export NASD_DATA_DIR=/tmp/nasd NASD_COOKIE_SECURE=false
nasd --host 127.0.0.1 --port 8741
curl -s http://127.0.0.1:8741/api/v1/system/status
curl -s -X POST http://127.0.0.1:8741/api/v1/system/setup -H 'Content-Type: application/json' \
  -d '{"hostname":"nas","admin_username":"admin","admin_password":"longpassword12","timezone":"UTC"}'
```

## What comes next (Phase 4 — wait for `continue`)

SvelteKit web UI: dashboard, storage, shares, users, apps shell; wired to this API.

Reply **`continue`** for Phase 4.
