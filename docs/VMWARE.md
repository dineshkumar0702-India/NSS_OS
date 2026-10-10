# VMware Workstation — OpenNAS-Lite test VM

Use this guide after you have built the ISO (see [BUILD.md](BUILD.md) or below).

## Build the ISO on Windows (no reboot)

ISO builds need **Linux** (`live-build`). **You do not need WSL or a Windows reboot** if you use a Debian builder VM or GitHub Actions — see **[BUILD-NO-REBOOT.md](BUILD-NO-REBOOT.md)**.

Quick summary:

| Method | Reboot? |
|--------|---------|
| **Debian VM** + `build/scripts/debian-guest-build.sh` | No |
| **GitHub Actions** artifact | No |
| **WSL** `Build-Iso-Wsl.ps1` | Yes (first-time WSL) |
| **Docker** `build-iso-docker.sh` | Varies |

Output file:

`build\output\opennas-lite-bookworm-amd64.iso`

Verify checksum:

```bash
sha256sum -c build/output/opennas-lite-bookworm-amd64.iso.sha256
```

## Create the VM (Workstation 17+)

### Recommended test profile (matches low-end hardware target)

| Setting | Value |
|---------|--------|
| Guest OS | Other 64-bit |
| Firmware | **UEFI** (or BIOS for legacy test) |
| CPUs | 2 |
| Memory | 2048–4096 MB |
| Disk | 32 GB SCSI or NVMe (thin provisioned) |
| Network | NAT (or bridged for LAN discovery) |
| CD/DVD | Use ISO image → path to `opennas-lite-bookworm-amd64.iso` |

### Quick create (UI)

1. **File → New Virtual Machine** → Custom.
2. Hardware compatibility: Workstation 17.x.
3. Install from installer disc: select the OpenNAS ISO.
4. Guest: **Other** → **Other 64-bit**.
5. Name: `OpenNAS-Lite-Test`.
6. Firmware: **UEFI** (uncheck Secure Boot if the installer fails to boot).
7. Processors: **2**, memory: **2048 MB** (use 4096 for Standard profile + Docker tests).
8. Network: NAT.
9. I/O: LSI Logic SAS; disk: **SCSI 32 GB**, single file.
10. Finish → **Power on**.

### Sample VMX snippet

Copy [build/vmware/opennas-lite-test.vmx](../build/vmware/opennas-lite-test.vmx) and set `opennas-lite.iso` filename to your ISO path (avoid spaces in path).

## Install inside the VM

1. Boot from ISO; wait for live desktop (Openbox).
2. **Calamares** should autostart; if not, run `pkexec calamares` from a terminal.
3. Choose **Standard** profile for a typical lab NAS.
4. Partitioning: select the **virtual disk** (not the ISO); use erase/install workflow.
5. Create user → install → reboot → remove ISO from VM settings (or disconnect CD).

## After install

1. Note the VM IP (NAT): **VM → Settings → Network Adapter** or run `ip a` in the guest.
2. From the Windows host browser:
   - `https://<guest-ip>/` (Caddy with internal TLS — accept the warning), or
   - `https://opennas.local` if bridged networking and mDNS work.
3. Complete the **Setup** wizard, then sign in.

**SSH (optional):** Enable `ssh` in the guest if you unmasked it; default install masks SSH on live image — installed system may enable per profile.

## Lab flags (storage / Docker tests on virtual disks)

By default destructive operations are **simulated**. On a throwaway VM you can enable real pool operations:

```bash
sudo mkdir -p /etc/systemd/system/nasd.service.d
sudo tee /etc/systemd/system/nasd.service.d/vm-lab.conf <<'EOF'
[Service]
Environment=NASD_ALLOW_STORAGE_MUTATIONS=true
EOF
sudo systemctl daemon-reload
sudo systemctl restart nasd
```

Use only on VMs with no data to lose.

## Troubleshooting VMware

| Issue | Fix |
|-------|-----|
| Black screen after boot | VM Settings → Display → accelerate; or edit boot params `nomodeset` |
| UEFI shell only | Enable EFI; ensure ISO is connected; try BIOS firmware mode |
| Install very slow | Store VM on SSD; give 2+ CPUs and 4 GB RAM for install |
| No HTTPS / connection refused | `systemctl status nasd caddy`; check firewall |
| ISO build fails on `/mnt/c` | Clone repo inside WSL home (`~/NSS_OS`) for faster I/O |

## Next: physical hardware

After VMware validation, repeat install on target hardware using the same ISO. See [HARDWARE.md](HARDWARE.md) and [INSTALL.md](INSTALL.md).
