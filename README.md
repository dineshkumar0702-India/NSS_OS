# OpenNAS-Lite

Bootable, installable open-source NAS operating system (Debian 12–based), designed for functional parity with consumer NAS platforms while running on ~10-year-old x86_64 hardware.

| Item | Value |
|------|--------|
| Codename | **OpenNAS-Lite** |
| Workspace | `NSS_OS` (this repository) |
| Current phase | **Phase 7 — Documentation** (complete) |
| Next steps | See [Roadmap](docs/ROADMAP.md) (hardening, OpenAPI, release) |

## Documentation

| Document | Description |
|----------|-------------|
| [Assumptions](docs/ASSUMPTIONS.md) | Defaults and decisions taken without prior Q&A |
| [Architecture overview](docs/architecture/README.md) | System context and navigation |
| [Block diagram](docs/architecture/block-diagram.md) | Components and data flows |
| [Modules](docs/architecture/modules.md) | Feature modules and dependencies |
| [Tech stack](docs/architecture/tech-stack.md) | Choices and trade-offs |
| [API design](docs/architecture/api-design.md) | REST/OpenAPI conventions |
| [Security model](docs/architecture/security-model.md) | Threat model and controls |
| [Data model](docs/architecture/data-model.md) | Persistent configuration schema |
| [Phase 1 summary](docs/PHASE1-SUMMARY.md) | Architecture deliverables |
| [Build guide](docs/BUILD.md) | ISO build and QEMU smoke test |
| [Phase 2 summary](docs/PHASE2-SUMMARY.md) | Build system deliverables |
| [Phase 3 summary](docs/PHASE3-SUMMARY.md) | nasd / nasctl deliverables |
| [Phase 4 summary](docs/PHASE4-SUMMARY.md) | Web UI deliverables |
| [Phase 5 summary](docs/PHASE5-SUMMARY.md) | Backups, apps, VPN, notifications |
| [Testing matrix](docs/TESTING.md) | QEMU / OTA / RAID manual tests |
| [Phase 6 summary](docs/PHASE6-SUMMARY.md) | OTA, advisor, diagnostics |
| [Phase 7 summary](docs/PHASE7-SUMMARY.md) | User and operator documentation |
| [Install guide](docs/INSTALL.md) | ISO, Calamares, first boot |
| [Admin guide](docs/ADMIN.md) | Day-to-day appliance management |
| [Developer guide](docs/DEVELOPER.md) | `nasd`, web UI, tests, ISO |
| [Hardware compatibility](docs/HARDWARE.md) | RAM, disks, NICs, limits |
| [Roadmap](docs/ROADMAP.md) | Done vs planned features |
| [**Project memory (handoff)**](MEMORY.md) | Full context after reboot / new chat |

## Repository layout

```
NSS_OS/
├── MASTER_PROMPT.md          # Original product specification
├── README.md
├── LICENSE
├── THIRD-PARTY-LICENSES.md
├── docs/                     # Architecture and guides (Phase 1+)
├── openapi/                  # Canonical OpenAPI spec (stub in Phase 1)
├── build/                    # live-build, ISO CI (Phase 2)
├── config/                   # Ship defaults, profiles (Phase 2+)
├── src/
│   ├── daemon/               # `nasd` management service (Phase 3)
│   ├── cli/                  # `nasctl` (Phase 3)
│   └── web/                  # Management UI (Phase 4)
├── packaging/                # Debian packages, systemd units (Phase 3+)
├── apps/                     # App Center compose templates (Phase 5)
└── tests/                    # Integration and acceptance tests
```

## License

See [LICENSE](LICENSE). Third-party components are listed in [THIRD-PARTY-LICENSES.md](THIRD-PARTY-LICENSES.md).

## Quick build (Linux / WSL)

```bash
bash build/scripts/prepare-iso-assets.sh
sudo bash build/scripts/build-iso.sh
```

**Windows (no reboot):** [docs/GITHUB-ISO-BUILD.md](docs/GITHUB-ISO-BUILD.md) (GitHub Actions) or [docs/BUILD-NO-REBOOT.md](docs/BUILD-NO-REBOOT.md) (Debian builder VM).  
**VMware test:** [docs/VMWARE.md](docs/VMWARE.md).

```bash
bash build/scripts/qemu-smoke.sh
```

See [docs/BUILD.md](docs/BUILD.md) and [docs/INSTALL.md](docs/INSTALL.md).

## Status

Phases 1–7 complete: architecture, ISO build, `nasd`/`nasctl`, SvelteKit UI, advanced modules, OTA/hardening, and operator documentation. Safety flags default to **simulated** disk/Docker/upgrade operations until enabled on a real appliance — see [docs/ADMIN.md](docs/ADMIN.md).
