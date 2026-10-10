# Assumptions (Phase 1)

These defaults apply because the master prompt allows proceeding without blocking questions. Change any of them before Phase 2 if you want a different direction.

## Product and scope

1. **Repository name** is `NSS_OS`; **product codename** is **OpenNAS-Lite**. Marketing name and domain (`nas.local`) are placeholders.
2. **Functional parity** targets UGOS/UGOS Pro–class features as **open replacements**, not clones of proprietary UI, assets, or protocols beyond public standards (SMB, NFS, etc.).
3. **Phase 1 deliverable** is architecture documentation plus repo skeleton only—no ISO, no daemon code, no UI implementation.
4. **First supported architecture** is `amd64` only. ARM64 is out of scope until a later roadmap item.
5. **Single-node NAS** is the primary model; clustered HA is documented as future work only.

## Platform

6. **Base OS**: Debian 12 (bookworm) minimal, built with **debian-live** (`live-build`).
7. **Installer**: **Calamares** with custom branding and OpenNAS-Lite partitioning modules (RAID/pool wizard hooks in Phase 2–3).
8. **Init**: systemd with a dedicated `nas.slice` for management stack and aggressive disabling of desktop-oriented units on the installed system.
9. **Default storage profile** on install: **Btrfs** multi-device pools (RAID1/RAID5/RAID6/RAID10/JBOD) with mixed-size handling via **Btrfs profiles + per-volume subvolumes**, not a proprietary SHR binary format. **ext4 + mdadm + LVM** is the low-RAM alternate; **ZFS** is opt-in when RAM ≥ 8 GB and user accepts warnings.
10. **Kernel**: Debian `linux-image-amd64` (LTS/backports drivers added in build phase if needed for old NICs/HBAs).

## Management stack

11. **Backend daemon**: **Python 3.11+** with **FastAPI** (`nasd`), one process with asyncio workers and subprocess/supervisor integration for long jobs. Go was considered; Python wins for rapid integration with storage tooling, LDAP, and Ansible-style glue at acceptable idle cost when trimmed.
12. **CLI**: `nasctl` wraps the same REST API locally (Unix socket) and supports scripting/JSON output.
13. **Web UI**: **SvelteKit** static adapter, built assets served by **Caddy** on the appliance (reverse proxy to API, static files, optional app routes).
14. **API contract**: REST + OpenAPI 3.1; WebSocket channel for live metrics and job progress (defined in Phase 1, implemented Phase 3+).
15. **Local API bind**: Unix domain socket `/run/nasd/nas.sock` and loopback HTTP `127.0.0.1:8741` for Caddy upstream; remote access only via HTTPS/VPN as configured.

## Containers and virtualization

16. **Container runtime**: **Docker Engine** + **Compose v2** for App Center (broad template compatibility). Rootless Podman is a possible future alternate build flavor, not Phase 1–2.
17. **VMs**: **KVM/QEMU + libvirt**; UI hidden when `/proc/cpuinfo` lacks usable virtualization (with clear messaging). No hard dependency on VMs for core NAS features.
18. **App Center** ships curated **Compose templates** under `apps/`; one-click lifecycle is orchestrated by `nasd`, not a separate orchestrator.

## Media, backup, sync

19. **Backup engine**: **restic** (local snapshots) + **rclone** (cloud remotes); schedules and policies in `nasd`.
20. **Device sync**: **Syncthing** as optional package/app template.
21. **Media**: **Jellyfin** as App Center template; photo library uses filesystem + index DB in `nasd` (optional **Immich-lite** or lightweight gallery in Phase 5).
22. **AI photo features**: optional ONNX CPU models; disabled when install profile is **Minimal** or CPU benchmark fails threshold (detailed in Phase 5).

## Security and updates

23. **Firewall**: **nftables** with templates managed by `nasd`; **fail2ban** or **nftables set**-based ban for SSH/admin endpoints.
24. **Auth**: local users + **PAM**; Web UI session cookies + **TOTP** and **WebAuthn** for admins; SMB/NFS use system users/groups.
25. **HTTPS**: Caddy automatic internal CA for `.local`; **Let's Encrypt** when public hostname and DDNS are configured.
26. **Updates**: **Btrfs snapshot** of root subvolume `@` before package upgrade, or **A/B ext4** images on mdadm boot mirror—default install on Btrfs uses snapshot rollback; documented in Phase 6.

## Internationalization and UX

27. **UI language** at launch: **English only** (Hindi removed from scope; strings remain centralized in `src/web/src/lib/i18n.ts` for future locales).
28. **Hostname/mDNS**: `nas.local` via **Avahi**; default hostname `opennas`.

## Hardware profiles (install-time)

29. Three profiles: **Minimal** (2 GB RAM, no Docker default, no ZFS, no VMs), **Standard** (4 GB, Docker + most apps), **Full** (8 GB+, ZFS/VM/AI optional modules offered).
30. **Idle RAM target** &lt; 400 MB is achieved by not starting Docker, Jellyfin, or VM libvirt until enabled.

## Legal and licensing

31. **Project license**: **GPL-3.0-or-later** for OpenNAS-Lite–authored code; documentation under **CC-BY-SA-4.0** where noted.
32. **AGPL** apps (e.g. some network services) run as separate containers; we do not link proprietary code into GPL components.

## Out of scope for Phase 1

- CI runners, ISO hashes, QEMU test scripts (Phase 2).
- LDAP/AD join implementation details beyond API stubs (Phase 5 optional module).
- Exact package versions pin list (Phase 2 `build/config/package-lists/`).
