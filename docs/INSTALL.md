# OpenNAS-Lite — Installation guide

This guide covers obtaining the ISO, preparing hardware, running the installer, and completing first-time setup. For building your own ISO, see [BUILD.md](BUILD.md).

## Before you begin

| Requirement | Notes |
|-------------|--------|
| Architecture | **x86_64 (amd64)** only in current releases |
| RAM | **2 GB** minimum (live/install); **4 GB+** recommended for Standard profile |
| Boot | Legacy BIOS or UEFI (both supported on the hybrid ISO) |
| Network | Ethernet recommended for first setup; Wi‑Fi depends on chipset/drivers |
| Data disks | Separate from OS disk when possible; **back up** before any erase/pool operation |

**Data safety:** Pool creation, disk erase, and system updates use **dry-run** and **confirm** flows in the management UI. Read every confirmation screen. Wrong disk selection can destroy data.

## Obtain the ISO

**Option A — Release artifact (when published)**  
Download `opennas-lite-bookworm-amd64.iso` and the matching `.sha256` from your distribution channel. Verify:

```bash
sha256sum -c opennas-lite-bookworm-amd64.iso.sha256
```

**Option B — Build from source (Linux / WSL2)**

```bash
cd /path/to/NSS_OS
sudo bash build/scripts/build-iso.sh
# Output: build/output/opennas-lite-bookworm-amd64.iso
```

## Write the installer media

Use any tool that writes a **raw** ISO image (not “copy files” to a FAT stick):

- **Linux:** `sudo dd if=opennas-lite-bookworm-amd64.iso of=/dev/sdX bs=4M status=progress && sync`
- **Windows:** Rufus, Ventoy, or `dd` in WSL targeting the USB device

Replace `/dev/sdX` with the correct block device. **Double-check the device** — `dd` is destructive.

## Boot the installer

1. Attach the USB drive (or mount the ISO in a VM).
2. Boot the machine and select the USB / optical drive.
3. Choose **OpenNAS-Lite** from the GRUB menu (BIOS or UEFI entry as appropriate).
4. Wait for the live graphical session (LightDM → Openbox).

Optional QEMU smoke test before real hardware:

```bash
bash build/scripts/qemu-smoke.sh          # BIOS
MODE=uefi bash build/scripts/qemu-smoke.sh  # UEFI
```

**VMware Workstation on Windows:** build the ISO with WSL or Docker, then follow [VMWARE.md](VMWARE.md).

## Run Calamares

1. Launch **Install OpenNAS-Lite** (autostart or desktop icon).
2. **Welcome / locale:** English (default); timezone and keyboard as needed.
3. **Install profile** (OpenNAS custom step):
   - **Minimal** — low RAM, fewer services, no Docker by default.
   - **Standard** — recommended home NAS (Docker App Center enabled).
   - **Full** — more packages; use only if you have RAM and disk headroom.
4. **Partitioning** (OpenNAS partition job):
   - Pick the **OS target disk** carefully.
   - **Erase** workflows replace existing partitions on the selected disk.
   - For multi-disk pools, complete OS install first; use the **web Storage** manager after first boot for pool creation (with dry-run + confirm).
5. **User account:** Create the initial admin Linux user (used for setup and optional SSH).
6. **Summary → Install.** When finished, reboot and remove install media.

See [HARDWARE.md](HARDWARE.md) for disk, RAID, and RAM guidance.

## First boot

1. The system should boot to the installed OpenNAS-Lite entry in GRUB.
2. On the LAN, the host may appear as **`opennas.local`** (Avahi/mDNS) if your network allows `.local` names.
3. From another computer on the same subnet, open:
   - **`https://opennas.local`** or **`https://<appliance-ip>`**
   - If TLS is not yet configured, the installer may expose HTTP on the LAN only during setup — follow on-screen warnings.

## Setup wizard (web UI)

On first visit, the **Setup** flow runs when the appliance is not yet configured:

1. Set the **administrator** account for the web UI (distinct from the Linux user if you chose that separation).
2. Set **hostname** and basic **network** preferences if prompted.
3. Review **install profile** summary and finish.

After setup, sign in at **Login** and open the **Dashboard**.

## Post-install checklist

| Step | Where |
|------|--------|
| Confirm time/NTP | Dashboard / System (when exposed) |
| Create storage pool | **Storage** — always run **dry-run** first |
| Create SMB shares | **Shares** |
| Add users | **Users** |
| Enable firewall rules for WAN | **Security** / advisor remediation |
| Install apps | **Apps** (Docker; see admin guide) |
| Configure backups | **Backups** |
| Check for updates | **Updates** (dry-run before apply) |

## Troubleshooting

| Symptom | Things to try |
|---------|----------------|
| No boot menu | Enable USB boot; try UEFI vs Legacy mode |
| Black screen after boot | Safe graphics: boot with `nomodeset` kernel param (one-time GRUB edit) |
| Cannot open web UI | Ping appliance IP; check cable/VLAN; try `http://<ip>:8741` only from localhost SSH |
| Wrong disk wiped | Prevention only: use QEMU first; never install with external USB disks attached unless intentional |

**Local diagnostics (SSH on appliance):**

```bash
systemctl status nasd caddy
nasctl status    # if nasctl is installed and API is reachable
journalctl -u nasd -n 100 --no-pager
```

For deeper checks, see [ADMIN.md](ADMIN.md) (diagnostics bundle) and [TESTING.md](TESTING.md).

## Uninstall / replace OS

OpenNAS-Lite does not ship a dedicated uninstaller. To remove it, back up data, then install another OS or repartition the boot disk from live media. **Data volumes** on separate disks may remain intact if you do not reformat them.

## Next steps

- Day-to-day operation: [ADMIN.md](ADMIN.md)
- Hardware limits and tested profiles: [HARDWARE.md](HARDWARE.md)
- Contributing or hacking on the stack: [DEVELOPER.md](DEVELOPER.md)
