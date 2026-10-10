# Phase 5 summary — Advanced modules

## Language

- Web UI is **English only** (Hindi removed per product direction).
- ISO locale hooks trimmed to English.

## What was done

### `nasd` API

| Area | Endpoints |
|------|-----------|
| Snapshots | `GET/POST /api/v1/storage/snapshots` |
| Backups | `GET/POST /api/v1/backups/policies`, `POST /api/v1/backups/run` (restic job, simulated by default) |
| App Center | `GET /api/v1/apps/catalog`, `GET/POST /api/v1/apps/instances`, `POST .../action` |
| VMs | `GET/POST /api/v1/vms` (stub when no KVM) |
| VPN | `GET/PUT /api/v1/vpn/wireguard` (config in DB; apply in Phase 6) |
| Notifications | `GET/PUT /api/v1/notifications/channels` |

Job types: `snapshot.create`, `backup.run`, `app.install|start|stop|restart|uninstall`.

Safety: `NASD_ALLOW_DOCKER_OPS=false` (default) simulates Docker; `NASD_ALLOW_STORAGE_MUTATIONS` unchanged.

### App templates

- `apps/jellyfin/`, `apps/pihole/` with `METADATA.json` + `compose.yaml`.

### Web UI

- `/apps` — catalog + instances
- `/backups`, `/notifications`, `/vpn`
- Nav updated; i18n simplified to English `t()` helper.

### Tests

- `tests/test_phase5.py` — catalog + backup job.

## Configuration

| Variable | Default |
|----------|---------|
| `NASD_APPS_DIR` | `/usr/share/opennas/apps` (dev/tests use repo `apps/`) |
| `NASD_ALLOW_DOCKER_OPS` | `false` |

## What comes next (Phase 6 — wait for `continue`)

OTA updates/rollback, security advisor, hardening, QEMU/RAID test matrix, benchmarks.

Reply **`continue`** for Phase 6.
