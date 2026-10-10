# Phase 7 summary — Documentation

## What was done

1. **[INSTALL.md](INSTALL.md)** — ISO obtain/build, media write, Calamares flow, first boot, setup wizard, troubleshooting.
2. **[ADMIN.md](ADMIN.md)** — Web/`nasctl` access, storage safety, shares, users, apps, backups, updates, advisor, config export/import, diagnostics, `NASD_*` flags.
3. **[DEVELOPER.md](DEVELOPER.md)** — Repo layout, `nasd` and web dev, tests, App Center, ISO integration.
4. **[HARDWARE.md](HARDWARE.md)** — amd64, RAM profiles, storage/network guidance, limitations, test workflow.
5. **[ROADMAP.md](ROADMAP.md)** — Phase completion table and feature status (done / planned / future).
6. **README.md** — Updated phase status and documentation index.

## How to test

Documentation is prose — verify accuracy against the tree:

```bash
cd src/daemon && python -m pytest ../../tests -q
```

Spot-check links from [README.md](../README.md) and run install steps in QEMU per [INSTALL.md](INSTALL.md) and [BUILD.md](BUILD.md).

## Master prompt completion

Phases **1–7** from [MASTER_PROMPT.md](../MASTER_PROMPT.md) now have corresponding deliverables in this repository. Further work is **roadmap** items (production hardening, OpenAPI parity, libvirt, translations), not additional master-prompt phases.

## What comes next

No further phased prompt is defined. Use [ROADMAP.md](ROADMAP.md) for prioritization. Reply with a specific goal (e.g. “wire OTA to real apt”, “expand OpenAPI”, “init git and CI release”) to continue implementation work.
