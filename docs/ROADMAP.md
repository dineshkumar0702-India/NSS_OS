# OpenNAS-Lite — Roadmap

High-level plan aligned with [MASTER_PROMPT.md](../MASTER_PROMPT.md) and [ASSUMPTIONS.md](ASSUMPTIONS.md). Dates are **not** commitments — items move with contributor capacity and hardware validation.

## Legend

| Status | Meaning |
|--------|---------|
| **Done** | Delivered in this repository (may be simulation/stub where noted) |
| **In progress** | Partial implementation or docs-only |
| **Planned** | Agreed direction, not started |
| **Future** | Desirable, not scoped |

---

## Phase delivery (master prompt)

| Phase | Scope | Status |
|-------|--------|--------|
| 1 | Architecture docs, repo skeleton | **Done** |
| 2 | live-build ISO, Calamares, CI build | **Done** |
| 3 | `nasd` + `nasctl`, core APIs, tests | **Done** |
| 4 | SvelteKit web UI | **Done** |
| 5 | Backups, snapshots, apps, VPN, notifications, VM stub | **Done** |
| 6 | OTA, advisor, diagnostics, test matrix | **Done** |
| 7 | Install/admin/developer docs, hardware list, roadmap | **Done** (this document set) |

---

## Core platform

| Item | Status | Notes |
|------|--------|-------|
| Debian 12 base, hybrid ISO | **Done** | `build/live-build/` |
| BIOS + UEFI boot | **Done** | QEMU scripts |
| Calamares + OpenNAS profile/partition | **Done** | Extend for advanced RAID UX |
| Avahi `*.local` | **Done** | Profile-dependent |
| Caddy TLS termination | **Done** | Operator must configure real certs |
| nftables + fail2ban | **Done** | Standard/Full profiles |

## Storage

| Item | Status | Notes |
|------|--------|-------|
| Disk inventory API | **Done** | |
| Btrfs pool create/extend (API) | **Done** | Real ops need `NASD_ALLOW_STORAGE_MUTATIONS` |
| Dry-run + confirm tokens | **Done** | |
| ext4/mdadm/LVM path | **Planned** | Documented in architecture |
| ZFS opt-in | **Planned** | RAM gating + warnings |
| SMART monitoring UI | **Planned** | |
| Power-loss test playbook | **Done** | [TESTING.md](TESTING.md) manual |

## Data services

| Item | Status | Notes |
|------|--------|-------|
| SMB shares | **Done** | Samba config render |
| NFS / iSCSI | **Future** | |
| Snapshots | **Done** | Job-based |
| File browser (scoped) | **Done** | |

## Identity and security

| Item | Status | Notes |
|------|--------|-------|
| Local users + sessions | **Done** | |
| TOTP / WebAuthn | **Planned** | In security model |
| RBAC fine-grained roles | **Planned** | |
| Security advisor | **Done** | |
| LUKS / fscrypt UI | **Future** | |

## Apps and containers

| Item | Status | Notes |
|------|--------|-------|
| App Center catalog | **Done** | `apps/` templates |
| Docker lifecycle jobs | **Done** | `NASD_ALLOW_DOCKER_OPS` |
| Jellyfin / Pi-hole templates | **Done** | |
| Rootless Podman flavor | **Future** | |
| Photo AI / Immich-lite | **Future** | Phase 5 optional scope |

## Backup and sync

| Item | Status | Notes |
|------|--------|-------|
| restic policies + jobs | **Done** | |
| rclone cloud remotes | **Planned** | |
| Syncthing template | **Planned** | |

## Network and VPN

| Item | Status | Notes |
|------|--------|-------|
| Interface management API | **Done** | |
| WireGuard config API | **Done** | Host apply hardening **Planned** |
| Reverse proxy for apps | **Planned** | Caddy routes |

## Virtualization

| Item | Status | Notes |
|------|--------|-------|
| VM list/create API | **Stub** | libvirt integration **Planned** |

## Updates and operations

| Item | Status | Notes |
|------|--------|-------|
| OTA check/apply dry-run | **Done** | |
| Btrfs rollback integration | **Partial** | Script + simulated job |
| Config export/import | **Done** | No password hashes |
| Diagnostics bundle | **Done** | |
| Web UI: Updates / Security | **Done** | |

## Web UI and i18n

| Item | Status | Notes |
|------|--------|-------|
| Dashboard, storage, shares, users, files | **Done** | |
| Apps, backups, VPN, notifications | **Done** | |
| Additional languages | **Future** | English-only by product choice |
| WebSocket live metrics | **Planned** | API design Phase 1 |

## API and quality

| Item | Status | Notes |
|------|--------|-------|
| OpenAPI 3.1 canonical spec | **Partial** | `openapi/openapi.yaml` stub — expand |
| Pytest API suite | **Done** | 13+ tests |
| ISO CI workflow | **Done** | |
| Release signing / SBOM | **Planned** | |

## Hardware and ports

| Item | Status | Notes |
|------|--------|-------|
| amd64 | **Done** | |
| ARM64 | **Future** | |
| HA cluster | **Future** | Single-node only |

---

## Suggested near-term priorities

1. **Production hardening:** wire real Btrfs snapshot + `apt` in OTA when `NASD_ALLOW_SYSTEM_UPGRADE=true`; validate rollback on installed root layout.
2. **OpenAPI parity** with implemented routes for external integrators.
3. **ISO staging:** ensure built web UI and `nasd` package land in `includes.chroot` for end-to-end appliance images.
4. **Storage UX:** Calamares multi-disk wizard alignment with post-install pool API.
5. **libvirt** VM lifecycle behind capability detection.

---

## How to influence the roadmap

- Open issues or PRs with hardware reports, API gaps, or doc fixes.
- Propose app templates under `apps/` with Compose files and clear licenses.
- Keep destructive features behind dry-run + confirm — non-negotiable for merge.

See [DEVELOPER.md](DEVELOPER.md) for contribution workflow.
