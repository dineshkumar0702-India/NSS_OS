# Tech stack

Choices below follow [ASSUMPTIONS.md](../ASSUMPTIONS.md). Deviations from the master prompt are called out explicitly.

## Summary table

| Area | Choice | Alternatives considered |
|------|--------|-------------------------|
| Base OS | Debian 12 bookworm | Ubuntu Server (heavier metapackages) |
| ISO build | debian-live (`live-build`) | Custom debootstrap only (less installer integration) |
| Installer | Calamares | Custom TUI (slower to ship) |
| Init | systemd | OpenRC (poor Docker/libvirt integration) |
| Kernel | Debian amd64 LTS | Mainline (worse HBA/NIC stability on old HW) |
| Default FS | Btrfs | ext4+mdadm default rejected for snapshot story |
| Low-RAM FS | ext4 + mdadm + LVM | — |
| Optional FS | OpenZFS (DKMS) | — |
| Swap | zram + optional swapfile | disk swap only (wear on flash) |
| Management API | Python 3.11 + FastAPI | Go (faster binary, slower feature velocity) |
| API server | uvicorn + gunicorn optional | hypercorn |
| Config DB | SQLite 3 (WAL) | etcd (overkill), plain YAML only (no queries) |
| Job queue | SQLite `jobs` table + asyncio workers | Redis (RAM cost) |
| Reverse proxy | Caddy 2 | nginx (more manual TLS) |
| Web UI | SvelteKit (static) | Vue (larger default bundle), React |
| CSS | Tailwind or lightweight custom tokens | Heavy component libraries |
| SMB | Samba 4.x | ksmbd (immature for Time Machine) |
| NFS | nfs-kernel-server | — |
| Firewall | nftables | iptables-legacy |
| Containers | Docker Engine + Compose v2 | Podman (Phase 2 focus on Docker) |
| VMs | QEMU/KVM + libvirt | — |
| Backup | restic + rclone | Borg (excellent but narrower cloud story) |
| Sync | Syncthing | — |
| VPN | WireGuard | OpenVPN (heavier) |
| mDNS | Avahi | — |
| Monitoring | Custom collectors + optional Netdata template later | Netdata default (RAM) |
| Tests | pytest, playwright (UI later) | — |

## Justification highlights

### Debian + live-build

Reproducible, familiar package set, broad hardware support, and Calamares integration are well documented. Target ISO ≤ 1.5 GB is achievable with a minimal package list and compressed live layer.

### Btrfs as default

Snapshots, send/receive, and subvolumes align with backup and OTA rollback without a separate volume manager UI for the common case. **Risk**: btrfs raid5/6 has historical parity caveats—we surface warnings and recommend raid1/raid10 for critical data.

### FastAPI + SQLite

Idle memory stays low with a single worker when tuned; SQLite avoids another daemon. **Risk**: write contention under heavy job logging—mitigate with WAL, batch writes, and optional log rotation to files.

### SvelteKit static

Pre-rendered UI keeps RAM near zero for the frontend process (Caddy serves files only). Bundle budget &lt; 3 MB gzipped is realistic with code splitting and no charting bloat on first paint.

### Caddy

Automatic HTTPS and simple reverse_proxy to `127.0.0.1:8741` reduce misconfiguration. Internal CA for `.local` avoids browser warnings in LAN lab setups (admin imports CA once).

### Docker for App Center

Compose templates are portable and match user expectations from other NAS products. **Risk**: Docker idle cost—mitigate by not enabling Docker in Minimal profile until user opts in.

## Old-hardware performance tactics

| Tactic | Implementation |
|--------|----------------|
| zram | `zram-generator` or systemd zram swap |
| Service trimming | `systemctl disable` bluetooth, cups, etc. |
| cgroup limits | `nas.slice`, Docker `--memory` defaults in App Center |
| I/O priority | `ionice` on scrub/backup jobs |
| Lazy UI | Dashboard polls at adaptive intervals; WebSocket for active jobs only |
| Capability gating | Skip loading ONNX, ZFS, libvirt packages in Minimal image flavor |

## Third-party license hotspots

| Component | License | Notes |
|-----------|---------|-------|
| Debian packages | GPL/LGPL/various | See image manifest Phase 2 |
| Samba | GPL-3 | — |
| Docker | Apache-2.0 | CLI; Moby engine |
| Jellyfin | GPL-2 | Container image |
| Syncthing | MPL-2.0 | — |
| Caddy | Apache-2.0 | — |
| Svelte | MIT | — |

Full list maintained in [THIRD-PARTY-LICENSES.md](../../THIRD-PARTY-LICENSES.md).

## Deviation log

| Prompt text | Decision | Reason |
|-------------|----------|--------|
| “Python or Go” | Python FastAPI | Faster integration phase; acceptable with trimming |
| “Caddy or nginx” | Caddy | TLS and config ergonomics |
| “Svelte/Vue/Preact” | SvelteKit | Smallest production bundle path |
| SHR-like | Btrfs multi-device + documentation | No proprietary on-disk format |

## Risks (architecture)

| Risk | Severity | Mitigation |
|------|----------|------------|
| Data loss on pool create | Critical | Two-step confirm, dry-run plan JSON, logging |
| API CSRF/session theft | High | HTTPS, SameSite cookies, optional 2FA |
| Docker escape | High | Non-root where possible, AppArmor default docker profile |
| ZFS RAM pressure | High | Gate on 8 GB + warning |
| AGPL container network | Medium | Document; user enables apps knowingly |
