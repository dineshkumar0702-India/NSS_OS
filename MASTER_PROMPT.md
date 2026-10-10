ROLE
You are a senior Linux systems engineer, NAS OS architect, and full-stack
developer with deep experience in Debian live-build, ZFS/Btrfs/mdadm, Samba,
Docker, KVM, and web UI development. You write production-grade, tested,
well-documented code.

OBJECTIVE
Design and build a bootable, installable NAS operating system (ISO image),
codename "OpenNAS-Lite", that:

1. Matches the feature set of Ugreen's UGOS / UGOS Pro (functional parity, not
a code copy; do NOT use Ugreen's proprietary code, assets, or branding).
2. Runs smoothly on \~10-year-old hardware (circa 2015).
3. Is fully open-source friendly, reproducible to build, and easy to install
on any x86\_64 PC or old server.

TARGET HARDWARE BASELINE (must run well on this)

* CPU: x86\_64 dual-core, e.g. Intel Celeron J1900 / Core 2 Duo / i3-4xxx /
AMD Athlon II. No dependence on AVX2, AES-NI, or hardware virtualization
for core features (use them if present, degrade gracefully if absent).
* RAM: 2 GB minimum (idle OS under 400 MB), 4 GB recommended.
Optional ZFS mode requires 8 GB; default must be Btrfs/ext4+mdadm for
low-RAM systems.
* Boot: both Legacy BIOS and UEFI; boot from USB/SATA DOM/SSD/HDD.
* Storage: SATA/SAS/NVMe, 1 to 12 drives, mixed sizes.
* Network: 1 GbE minimum; support Wi-Fi as optional, USB NICs, 2.5G/10G
where drivers exist.
* Install footprint: OS partition <= 8 GB; ISO <= 1.5 GB.

BASE SYSTEM DECISIONS (justify any deviation)

* Base: Debian 12 "bookworm" (or latest stable) minimal, built via
debian live-build with a custom installer (Calamares or a lightweight
custom TUI installer).
* Kernel: Debian LTS kernel with broad legacy driver support
(AHCI, SAS HBAs, old Realtek/Intel NICs, USB storage).
* Init: systemd with aggressive service trimming; zram swap enabled.
* Filesystems: Btrfs (default), ext4+mdadm+LVM, optional ZFS (OpenZFS DKMS).
* Backend: Python (FastAPI) or Go for the management daemon;
avoid heavy runtimes (no Electron, no JVM).
* Frontend: lightweight SPA (Svelte/Vue/Preact) served by Caddy or nginx;
total UI bundle under 3 MB; responsive for desktop and mobile; dark/light
theme; i18n-ready (include English).
* Container runtime: Docker (or Podman) with a simple App Center.
* VMs: KVM/QEMU + libvirt, shown only when CPU virtualization is available.

FEATURE PARITY CHECKLIST (implement each as a module)
A. Installation and Setup

* Bootable ISO installer, guided disk selection, RAID/pool wizard,
first-boot setup wizard (admin account, hostname, network, timezone).
* Network discovery: web UI at http://nas.local (mDNS/Avahi) plus a
desktop discovery tool concept (optional).
B. Storage Management
* Storage pools and volumes; RAID 0/1/5/6/10, JBOD, SHR-like mixed-size
support (via Btrfs or mdadm+LVM design).
* Drive hot-swap handling, SMART monitoring and alerts, disk health
dashboard, scrubbing/balance schedules, SSD cache (lvmcache/bcache),
volume expansion and RAID migration, disk hibernation/spin-down.
* Snapshots with scheduled retention and one-click restore.
C. File Services
* SMB (Samba) with Time Machine support, NFS, FTP/SFTP, WebDAV, rsync,
iSCSI target (optional module).
* Web File Manager (upload, download, preview, share links with
expiry/password, trash/recycle bin, search).
* Shared folders with ACLs, quotas, user/group management,
LDAP/AD join (optional).
D. Backup and Sync
* Local, remote, and cloud backup (restic/rclone: S3, Backblaze, Google
Drive, OneDrive, SFTP), scheduled jobs, versioning, integrity checks.
* Phone auto-backup via a companion protocol (WebDAV/Nextcloud-compatible
endpoint), PC backup (client-side), Time Machine.
* Two-way sync between NAS devices (Syncthing-based).
D2. Media and Photos
* Photo album with timeline, folders, albums, sharing, and EXIF/map view.
AI features (face/object recognition, OCR) must be an OPTIONAL module,
auto-disabled on weak CPUs, using lightweight models (ONNX/CPU only).
* Media server (Jellyfin) with optional hardware transcoding (Intel
QuickSync/VAAPI if present), DLNA.
E. Apps and Virtualization
* App Center: curated Docker Compose templates (Nextcloud, Jellyfin,
Home Assistant, Pi-hole, qBittorrent, Vaultwarden, Immich-lite etc.),
one-click install/update/uninstall, resource limits per app.
* VM manager (create, snapshot, console via noVNC).
* Docker/Compose management UI, image/volume/network management.
F. Remote Access and Networking
* Secure remote access: WireGuard VPN, Tailscale/Cloudflare Tunnel
integration, DDNS, Let's Encrypt certificates, reverse proxy manager.
* Network settings: static IP, bonding/LACP, VLAN, IPv6, Wi-Fi,
port forwarding hints/UPnP.
G. Security
* Firewall UI (nftables), fail2ban-style IP blocking, 2FA (TOTP, WebAuthn),
HTTPS by default, encrypted volumes/folders (LUKS/fscrypt), audit logs,
antivirus (ClamAV, optional/scheduled), security advisor dashboard,
automatic security updates.
H. System and Monitoring
* Dashboard: CPU, RAM, network, disk IO, temperatures, fan control (where
supported), resource monitor per app/container.
* Notifications: email, Telegram, Discord, webhook, push.
* UPS support (NUT), scheduled power on/off, Wake-on-LAN, LED/status
control hooks.
* Atomic OTA updates with rollback (A/B or Btrfs snapshot-based),
config export/import, CLI tool ("nasctl"), REST API with OpenAPI docs.
* Syslog viewer, diagnostics bundle generator.

OLD-HARDWARE PERFORMANCE REQUIREMENTS (hard constraints)

* Idle RAM < 400 MB (no containers running); cold boot to web UI < 60 s on
HDD, < 30 s on SSD.
* Web UI first load < 3 s on LAN at 2 GB RAM Celeron J1900.
* Heavy features (AI photos, transcoding, VMs, ZFS, ClamAV) must be
opt-in modules with capability detection and clear warnings.
* Use cgroup limits, nice/ionice, systemd slices to keep file serving
responsive under load.
* Provide a "hardware compatibility check" at install time that recommends
a profile: Minimal / Standard / Full.

DELIVERABLES (work in phases; finish each phase before the next)
Phase 1 - Architecture: block diagram, module list, tech stack choices with
justification, repo layout, API design, security model, data model.
Phase 2 - Build system: complete live-build config, package lists, hooks,
installer, bootloader setup (BIOS+UEFI), CI script to produce the ISO,
QEMU test instructions.
Phase 3 - Core daemon and CLI: storage, users, shares, services, network,
with real code, unit tests, and systemd units.
Phase 4 - Web UI: dashboard, storage manager, file manager, shares, users,
apps; real code, not mockups.
Phase 5 - Advanced modules: backup, snapshots, App Center, VM, VPN,
notifications, photos/media.
Phase 6 - Hardening, update/rollback mechanism, testing matrix (BIOS/UEFI,
1-12 disks, RAID failure and rebuild, power-loss tests), benchmarks on
low-end hardware profiles (QEMU with 2 vCPU / 2 GB).
Phase 7 - Documentation: install guide, admin guide, developer guide,
hardware compatibility list, roadmap.

OUTPUT RULES

* Show full file contents with file paths; no pseudo-code or "..." in
critical files. Use code blocks per file.
* Explain trade-offs briefly; flag risks (data loss, security) clearly.
* Prefer proven open-source components over reinventing the wheel.
* Include automated tests and acceptance criteria for each module.
* All user data safety comes first: never run destructive disk operations
without explicit confirmation flows, dry-run modes, and logging.
* Respect licenses (GPL, AGPL, etc.) and list all third-party components
with their licenses.
* At the end of each phase, give: (1) what was done, (2) how to test it,
(3) what comes next. Then wait for my "continue".

START NOW with Phase 1. Ask me at most 5 clarifying questions first only if
critical; otherwise state your assumptions and proceed.

