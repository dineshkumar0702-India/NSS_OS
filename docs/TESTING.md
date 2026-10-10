# Testing matrix (Phase 6)

Run on **Linux** with QEMU; ISO from [BUILD.md](BUILD.md).

## Automated helpers

```bash
bash build/scripts/qemu-smoke.sh          # BIOS
MODE=uefi bash build/scripts/qemu-smoke.sh
bash build/scripts/qemu-matrix.sh         # BIOS + UEFI + benchmark hook
bash build/scripts/qemu-benchmark.sh      # 2 vCPU / 2 GB RAM timing
cd src/daemon && python -m pytest ../../tests -q
```

## Boot / firmware

| ID | Case | Pass criteria |
|----|------|----------------|
| B1 | Legacy BIOS boot live ISO | GRUB menu, live session starts |
| B2 | UEFI boot live ISO | shim/GRUB, no firmware error |
| B3 | Install to virtio disk | Calamares finishes, reboot |
| B4 | Installed BIOS boot | OpenNAS-Lite GRUB entry boots |
| B5 | Installed UEFI boot | ESP mounted, boots |

## Hardware profiles (QEMU)

| Profile | RAM | CPUs | Notes |
|---------|-----|------|-------|
| Minimal | 2048 | 2 | No Docker by default; UI responsive |
| Standard | 4096 | 2 | Docker + App Center |
| Full | 8192 | 4 | ZFS/VM options offered |

## Storage

| ID | Case | Pass criteria |
|----|------|----------------|
| S1 | 1 disk erase install | Root + data partitions |
| S2 | 2 disk btrfs raid1 plan | Dry-run shows commands, confirm_token |
| S3 | 12 virtio disks visible | `nasctl`/API lists all |
| S4 | Pool create without `NASD_ALLOW_STORAGE_MUTATIONS` | Job **simulated**, no mkfs |
| S5 | RAID rebuild | **Manual** — degrade mdadm array in VM, document rebuild steps |

## Power loss

| ID | Case | Pass criteria |
|----|------|----------------|
| P1 | Power off during apt upgrade | btrfs snapshot exists; rollback script documented |
| P2 | Power off during pool job | Job fails cleanly; no partial pool in DB without confirm |

## OTA updates

| ID | Case | Pass criteria |
|----|------|----------------|
| U1 | `POST /updates/apply` dry_run | Returns confirm_token + snapshot plan |
| U2 | Apply with confirm | Job success; `updates.last_apply` in DB |
| U3 | Rollback API | Returns simulated/manual guidance |
| U4 | `NASD_ALLOW_SYSTEM_UPGRADE=true` on lab only | Real apt upgrade |

## Security

| ID | Case | Pass criteria |
|----|------|----------------|
| X1 | `GET /security/advisor` | Score + findings list |
| X2 | Diagnostics bundle | ZIP download, no secrets in manifest |

## Performance targets (master prompt)

| Metric | Target | How to measure |
|--------|--------|----------------|
| Idle RAM | &lt; 400 MB | `free -m` on installed Minimal, no containers |
| Cold boot to web UI | &lt; 60 s HDD | Stopwatch after install on QEMU virtio HDD |
| Web UI first load | &lt; 3 s LAN | Browser devtools on dashboard |

## RAID failure (manual lab)

1. Create mdadm RAID1 in VM with two files or disks.
2. Fail one device: `mdadm --manage /dev/md0 --fail /dev/vdb`.
3. Verify degraded state in `/proc/mdstat`.
4. Remove and re-add device to rebuild.
5. Record timings and document in your run log.

Automating mdadm fault injection is environment-specific; this matrix treats **S5** as a documented manual procedure.
