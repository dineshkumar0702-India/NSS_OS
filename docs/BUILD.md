# Building OpenNAS-Lite (Phase 2)

ISO builds run on **Debian 12 or Ubuntu 22.04+** (native Linux or WSL2). Windows hosts:

- **WSL:** `wsl --install -d Debian` (Admin), reboot, then `.\build\scripts\Build-Iso-Wsl.ps1`
- **Docker:** `bash build/scripts/build-iso-docker.sh` (Docker Desktop)
- **VMware testing:** [VMWARE.md](VMWARE.md)

The ISO embeds `nasd`, the web UI (or a fallback page if npm is missing), and App Center templates via `prepare-iso-assets.sh`.

## Host prerequisites

```bash
sudo apt-get update
sudo apt-get install -y \
  live-build debootstrap squashfs-tools xorriso isolinux syslinux-utils \
  git rsync
```

Optional (QEMU smoke tests):

```bash
sudo apt-get install -y qemu-system-x86 ovmf
```

## Build steps

```bash
cd /path/to/NSS_OS
sudo bash build/scripts/stage-includes.sh   # optional; build-iso.sh calls this
sudo bash build/scripts/build-iso.sh
```

Output:

- `build/output/opennas-lite-bookworm-amd64.iso`
- `build/output/opennas-lite-bookworm-amd64.iso.sha256`
- Log: `build/logs/live-build.log`

Set a version label:

```bash
sudo BUILD_VERSION=1.0.0-rc1 bash build/scripts/build-iso.sh
```

## ISO contents (summary)

| Area | Implementation |
|------|----------------|
| Boot | GRUB **iso-hybrid** (legacy BIOS + UEFI via live-build) |
| Live session | LightDM → Openbox → Calamares (`pkexec`) |
| Installer | Calamares + custom **opennasprofile** (view) and **opennaspartition** (job) |
| Size budget | Hooks trim docs/locales; build warns if ISO &gt; 1536 MiB |

## QEMU smoke test

```bash
# BIOS boot, 2 GB RAM (matches master-prompt low-end profile)
bash build/scripts/qemu-smoke.sh

# UEFI
MODE=uefi bash build/scripts/qemu-smoke.sh
```

Custom ISO path:

```bash
ISO=/path/to/image.iso RAM_MB=4096 bash build/scripts/qemu-smoke.sh
```

### Acceptance checklist (manual)

1. ISO boots to graphical live session without kernel panic.
2. Calamares launches; profile step shows minimal/standard/full.
3. Partition step sees virtual disk; **erase** workflow completes on QEMU disk.
4. Installed system reboots; GRUB menu shows **OpenNAS-Lite** entry (BIOS and/or UEFI per test mode).
5. `http://opennas.local` or Avahi name resolves on LAN (after install on real hardware).

## OpenAPI lint (CI)

```bash
bash build/scripts/lint-openapi.sh
```

## Risks

- **Data loss**: Calamares erase mode wipes target disks. Test only on empty QEMU images or sacrificial hardware.
- **Package drift**: Debian mirror updates can change ISO size; adjust `opennas-installer.list.chroot` if over 1.5 GB.
- **Calamares QML**: `opennasprofile.qml` may need API tweaks for your exact Calamares 3.x point release—validate on first ISO build.

## Clean rebuild

```bash
cd build/live-build
sudo lb clean --purge
sudo rm -rf config/includes.chroot
```

Then run `build-iso.sh` again.
