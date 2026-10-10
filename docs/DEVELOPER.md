# OpenNAS-Lite — Developer guide

How to work on `nasd`, `nasctl`, the web UI, ISO build, and tests. Architecture deep-dives live under [architecture/](architecture/README.md).

## Repository map

| Path | Purpose |
|------|---------|
| `src/daemon/` | Python package `opennas-nasd` — FastAPI app, jobs, CLI entry `nasctl` |
| `src/web/` | SvelteKit static management UI |
| `openapi/openapi.yaml` | API contract (expand as endpoints stabilize) |
| `packaging/` | systemd units, Caddy snippet, rollback helper |
| `build/` | live-build, Calamares modules, ISO scripts |
| `apps/` | App Center Compose templates + `METADATA.json` |
| `config/` | Install profiles and seed JSON |
| `tests/` | Pytest integration tests against the API |

## Prerequisites

- **Python 3.11+**
- **Node.js 18+** and npm (for web UI; optional for daemon-only work)
- **Linux** or **WSL2** for ISO build and QEMU scripts
- Debian/Ubuntu packages for ISO: see [BUILD.md](BUILD.md)

## `nasd` development

```bash
cd src/daemon
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

pip install -e ".[dev]"
```

Run the API locally (isolated data dir):

```bash
export NASD_DATA_DIR=/tmp/nasd-dev
export NASD_COOKIE_SECURE=false
export NASD_APPS_DIR=/path/to/NSS_OS/apps
mkdir -p "$NASD_DATA_DIR"
nasd --host 127.0.0.1 --port 8741
```

Health check:

```bash
curl -s http://127.0.0.1:8741/api/v1/system/status | jq .
```

### Project layout (daemon)

```
src/daemon/nasd/
  app.py              # FastAPI factory
  settings.py         # Pydantic settings (NASD_* env)
  api/                # Route modules per domain
  core/               # Jobs, storage logic, updates, advisor, etc.
  models/             # SQLAlchemy models
  cli.py              # nasctl
```

**Adding an endpoint**

1. Implement handler in `nasd/api/<domain>.py`.
2. Register router in `nasd/api/router.py`.
3. Extend `openapi/openapi.yaml` when the contract is stable.
4. Add tests under `tests/` using the shared `client` fixtures in `conftest.py`.

**Jobs:** Long work should enqueue via `core/jobs.py` patterns (types like `storage.pool.create`, `backup.run`, `update.apply`). Respect safety flags in `settings.py`.

### Safety flags in dev

Keep defaults unless you are testing real side effects on a VM:

| Flag | Safe dev default |
|------|------------------|
| `NASD_ALLOW_STORAGE_MUTATIONS` | `false` |
| `NASD_ALLOW_DOCKER_OPS` | `false` |
| `NASD_ALLOW_SYSTEM_UPGRADE` | `false` |

## Web UI development

```bash
cd src/web
npm install
npm run dev
```

Vite proxies API requests to `http://127.0.0.1:8741` (see `vite.config.ts`). Run `nasd` in parallel.

Production build (output for packaging):

```bash
bash build/scripts/build-web.sh
# Artifacts: build/output/web/
```

UI strings use `src/lib/i18n.ts` (`t()` — English only). New pages: add a route under `src/routes/` and link from the layout nav.

## Tests

From repository root (recommended):

```bash
cd src/daemon
pip install -e ".[dev]"
python -m pytest ../../tests -q
```

`tests/conftest.py` sets `NASD_DATA_DIR`, `NASD_COOKIE_SECURE=false`, and `NASD_APPS_DIR` to the repo `apps/` directory.

**CI-style checks:**

```bash
bash build/scripts/lint-openapi.sh
```

Add tests for new API behavior; prefer dry-run paths that work with mutation flags off.

## ISO and appliance integration

1. Build ISO: [BUILD.md](BUILD.md).
2. Stage includes: `build/scripts/stage-includes.sh` (daemon, web assets, configs — follow script comments).
3. systemd: `packaging/systemd/nasd.service`.
4. Reverse proxy: `packaging/caddy/opennas.caddy`.

GitHub Actions workflow: `.github/workflows/build-iso.yml`.

## App Center templates

Each app directory contains:

- `METADATA.json` — id, name, version, compose project name
- `compose.yaml` — Docker Compose v2 file

`nasd` discovers templates from `NASD_APPS_DIR`. Instances are tracked in SQLite and materialized under `NASD_COMPOSE_PROJECTS_DIR` (`/var/lib/nasd/compose` on appliance).

## Coding conventions

- Match existing FastAPI dependency injection and SQLAlchemy session patterns (`get_db`, `get_session_factory()`).
- Never perform destructive disk or `apt` operations without dry-run + confirm token in the API layer.
- Log job steps through the job runner for operator visibility.
- GPL-3.0-or-later for project code; respect third-party licenses in [THIRD-PARTY-LICENSES.md](../THIRD-PARTY-LICENSES.md).

## Debugging

```bash
journalctl -u nasd -f
```

SQLite shell (dev only):

```bash
sqlite3 "$NASD_DATA_DIR/config.db" ".tables"
```

## Documentation

| Doc | Audience |
|-----|----------|
| [INSTALL.md](INSTALL.md) | Installers |
| [ADMIN.md](ADMIN.md) | Operators |
| [TESTING.md](TESTING.md) | QA / release |
| [ROADMAP.md](ROADMAP.md) | Planning |

Phase summaries (`PHASE*-SUMMARY.md`) record historical deliverables per master prompt.

## Getting help

- Spec: [MASTER_PROMPT.md](../MASTER_PROMPT.md)
- Assumptions: [ASSUMPTIONS.md](ASSUMPTIONS.md)
- API design notes: [architecture/api-design.md](architecture/api-design.md)
