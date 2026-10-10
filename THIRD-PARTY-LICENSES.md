# Third-party components

OpenNAS-Lite bundles and integrates many upstream projects. This file is a **Phase 1 index**; the Phase 2 build will generate a machine-readable manifest from the ISO package list.

## Base system (Debian 12)

| Component | License | Notes |
|-----------|---------|-------|
| Debian GNU/Linux | DFSG / mixed | See `/usr/share/doc/*/copyright` on installed system |
| Linux kernel | GPL-2.0 | `linux-image-amd64` |
| systemd | LGPL-2.1+ | |
| GRUB | GPL-3.0+ | |
| shim (UEFI) | BSD | When UEFI secure boot chain used |

## Storage and filesystems

| Component | License |
|-----------|---------|
| btrfs-progs | GPL-2.0 |
| mdadm | GPL-2.0 |
| LVM2 | GPL-2.0 LGPL-2.1 |
| OpenZFS (optional) | CDDL |

## File services

| Component | License |
|-----------|---------|
| Samba | GPL-3.0 |
| nfs-kernel-server | GPL / varied |

## Management stack (planned)

| Component | License |
|-----------|---------|
| Python | PSF |
| FastAPI | MIT |
| uvicorn | BSD |
| Caddy | Apache-2.0 |
| Svelte / SvelteKit | MIT |
| SQLite | Public domain |

## Operations

| Component | License |
|-----------|---------|
| Docker Engine | Apache-2.0 |
| QEMU/KVM | GPL-2.0 |
| libvirt | LGPL-2.1+ |
| WireGuard | GPL-2.0 |
| restic | BSD-2-Clause |
| rclone | MIT |
| Syncthing | MPL-2.0 |
| Jellyfin (container) | GPL-2.0 |
| fail2ban | GPL-2.0 |
| nftables | GPL-2.0 |
| Avahi | LGPL-2.1+ |
| Calamares | GPL-3.0 |

## App Center templates

Each template under `apps/` will ship a `LICENSE` or `METADATA.json` with upstream image license and source pointer. AGPL services run in containers without linking into GPL `nasd` code.

## Updating this file

Phase 2: add `scripts/generate-third-party-manifest.sh` output committed as `build/manifests/packages-licenses.json`.
