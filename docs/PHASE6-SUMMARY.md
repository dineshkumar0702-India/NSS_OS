# Phase 6 summary — Hardening & updates

## What was done

1. **OTA updates** — `GET /updates/status`, `POST /updates/check`, `POST /updates/apply` (dry-run + confirm), `POST /updates/rollback`; job type `update.apply` with Btrfs snapshot plan + apt upgrade (simulated unless `NASD_ALLOW_SYSTEM_UPGRADE=true`).
2. **Security advisor** — `GET /security/advisor` (score + findings).
3. **Config export/import** — `GET /system/config/export`, `POST /system/config/import` (no password hashes).
4. **Diagnostics** — `POST /system/diagnostics/bundle` → ZIP in `/run/nasd/`.
5. **Rollback helper** — [packaging/scripts/opennas-rollback.sh](../packaging/scripts/opennas-rollback.sh).
6. **Test matrix** — [TESTING.md](TESTING.md); [qemu-matrix.sh](../build/scripts/qemu-matrix.sh), [qemu-benchmark.sh](../build/scripts/qemu-benchmark.sh).
7. **Web UI** — `/updates`, `/security`.
8. **nasctl** — `updates`, `advisor`.
9. **Tests** — `tests/test_phase6.py`.

## Safety

| Flag | Default | Effect |
|------|---------|--------|
| `NASD_ALLOW_SYSTEM_UPGRADE` | `false` | Simulates snapshot + apt |
| `NASD_ALLOW_STORAGE_MUTATIONS` | `false` | Unchanged |
| `NASD_ALLOW_DOCKER_OPS` | `false` | Unchanged |

## How to test

```bash
cd src/daemon && python -m pytest ../../tests -q
```

API smoke (after login):

```bash
curl -s -b cookies.txt -X POST http://127.0.0.1:8741/api/v1/updates/apply -H 'Content-Type: application/json' -d '{"dry_run":true}'
curl -s -b cookies.txt http://127.0.0.1:8741/api/v1/security/advisor
```

## What came next (Phase 7)

Install, admin, developer, hardware, and roadmap docs — see [PHASE7-SUMMARY.md](PHASE7-SUMMARY.md).
