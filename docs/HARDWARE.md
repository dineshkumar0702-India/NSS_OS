# OpenNAS-Lite — Hardware compatibility

Guidance for choosing and validating hardware. This is a **living list** — community reports and CI QEMU profiles do not replace testing **your** disks and controllers before trusting production data.

## Supported platform (current)

| Component | Support |
|-----------|---------|
| CPU | **64-bit x86 (amd64)**; 2+ cores recommended |
| Firmware | **UEFI** and **legacy BIOS** boot |
| RAM | See profiles below |
| ARM / other arches | **Not supported** in current roadmap |

## Install profiles vs RAM

Profiles are selected in Calamares and recorded under `/var/lib/nasd/install-profile.json`.

| Profile | Minimum RAM | Typical use |
|---------|-------------|-------------|
| **Minimal** | 2 GB | File sharing, light services, no Docker |
| **Standard** | 4 GB | Home NAS + Docker App Center |
| **Full** | 8 GB+ | Extra packages; ZFS/VM options per flags |

**ZFS:** Opt-in only when RAM ≥ 8 GB and you accept memory overhead; default path is **Btrfs** on multi-disk pools.

**QEMU reference profile** (master prompt): 2 vCPU, 2 GB RAM — see `build/scripts/qemu-smoke.sh` and [TESTING.md](TESTING.md).

## Storage

### OS disk

- **64 GB+** SSD or HDD for OS + Docker images (SSD strongly recommended).
- Separate **data disks** from OS disk when possible.

### Data pools

| Layout | Notes |
|--------|--------|
| Single disk | JBOD / single-device Btrfs |
| Multi-disk Btrfs | RAID1, RAID1c3/RAID1c4, RAID10, RAID5/6 (kernel/fstab balance — understand reshape limits) |
| ext4 + mdadm + LVM | Alternate low-RAM path per architecture docs |
| ZFS | Optional; RAM and licensing trade-offs |

**Mixed-size disks:** Btrfs RAID1 profiles use capacity rules different from classic mdadm RAID1 — plan headroom and read [ADMIN.md](ADMIN.md) before expand/replace.

**HBAs and port multipliers:** Consumer SATA/JBOD enclosures vary widely. Verify `smartctl`, link speed, and whether the enclosure reports correct serials before destructive operations.

### USB / SD

- USB boot for **install media** only is fine.
- USB-attached **data pools** are discouraged (latency, surprise removal). Not recommended for production.

## Network

- **Intel** and common **Realtek** gigabit NICs on Debian 12 usually work out of the box.
- **10 GbE** depends on chipset (Mellanox/Intel often good; verify firmware).
- **Wi‑Fi** as primary NAS uplink is fragile; use Ethernet for management and SMB.

## Graphics

- Headless server install is typical. Live installer may need **`nomodeset`** on old or odd GPUs.

## Virtualization

KVM guests require CPU virtualization extensions (Intel VT-x / AMD-V) and enabled firmware settings. The UI hides or warns when `/proc/cpuinfo` lacks usable flags.

## Known limitations

| Area | Limitation |
|------|------------|
| Architecture | amd64 only |
| HA cluster | Single-node; no active-active cluster |
| SHR proprietary format | Not implemented — Btrfs/mdadm documented instead |
| VM management | API stub; libvirt integration incomplete |
| WireGuard | Config API present; full apply pipeline may need manual steps |
| Windows dev host | ISO build and QEMU via WSL2/Linux VM |

## Compatibility testing workflow

1. **QEMU** BIOS + UEFI smoke (`qemu-smoke.sh`, `qemu-matrix.sh`).
2. **Bare metal:** install to spare disk; validate NIC, SMART, and thermal behavior.
3. **Storage:** create pool with **dry-run**; confirm tokens; test scrub/balance on small arrays before production disks.
4. **Power loss:** only on disposable test arrays — see [TESTING.md](TESTING.md).

## Reporting hardware

When filing issues, include:

- CPU model, RAM, firmware (BIOS/UEFI)
- Disk models, connection (SATA/SAS/NVMe/USB), pool layout
- NIC chipset and driver (`ethtool -i`, `lspci -nn`)
- Install profile and OpenNAS version (`nasctl status`)

## References

- [INSTALL.md](INSTALL.md)
- [ASSUMPTIONS.md](ASSUMPTIONS.md) — default storage and stack choices
- [architecture/tech-stack.md](architecture/tech-stack.md)
