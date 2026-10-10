# Block diagram

## Physical deployment (typical appliance)

```mermaid
flowchart LR
  subgraph hw [Hardware]
    CPU[x86_64 CPU]
    RAM[RAM 2-32 GB]
    NIC[1GbE+ NICs]
    Disks[SATA/SAS/NVMe 1-12]
    USB[USB boot DOM]
  end

  subgraph firmware [Firmware]
    BIOS[Legacy BIOS or UEFI]
  end

  subgraph boot [Boot chain]
    GRUB[GRUB2]
    Kernel[Linux kernel]
    Initrd[initramfs]
  end

  subgraph os [Debian 12 rootfs]
    Systemd[systemd]
    Zram[zram swap]
    NASD[nasd]
    Caddy[Caddy]
    Svc[File and network services]
  end

  Disks --> GRUB
  USB --> GRUB
  BIOS --> GRUB
  GRUB --> Kernel --> Initrd --> Systemd
  Systemd --> Zram
  Systemd --> NASD
  Systemd --> Caddy
  Systemd --> Svc
  NASD --> Disks
  Svc --> Disks
  NIC --> Svc
  NIC --> Caddy
```

## Logical software layers

| Layer | Responsibility | Key components |
|-------|----------------|----------------|
| L0 Firmware | Boot device selection | UEFI/BIOS |
| L1 Bootloader | BIOS+UEFI, kernel cmdline | GRUB2, shim (UEFI) |
| L2 Kernel | Block, net, FS, cgroups | `linux-image-amd64`, optional `zfs`/`btrfs` |
| L3 Base OS | Packages, users, time, logging | Debian minimal, systemd, rsyslog/journald |
| L4 Storage stack | Pools, volumes, snapshots | btrfs tools, mdadm, LVM, optional OpenZFS |
| L5 Data services | Protocol endpoints | Samba, NFS, ProFTPD/vsftpd, sshd, WebDAV (Caddy/rclone serve) |
| L6 Platform | Containers/VMs | Docker, libvirt |
| L7 Management | API, UI, jobs, policy | `nasd`, Caddy, SvelteKit UI, `nasctl` |
| L8 Apps | User workloads | App Center Compose stacks |

## Management plane data flow

```mermaid
sequenceDiagram
  participant U as Admin browser
  participant C as Caddy
  participant D as nasd
  participant J as Job runner
  participant T as OS tools btrfs/smb/nft

  U->>C: HTTPS GET /api/v1/system/status
  C->>D: proxy (mTLS or UDS upstream)
  D->>D: auth session + RBAC
  D-->>U: JSON status

  U->>C: POST /api/v1/storage/pools (create preview)
  D->>D: validate + dry-run plan
  D-->>U: plan_id + warnings

  U->>C: POST /api/v1/storage/pools/confirm
  D->>J: enqueue job
  J->>T: btrfs/mdadm commands
  J->>D: progress events
  D-->>U: WebSocket job updates
```

## Network exposure

| Surface | Default bind | Purpose |
|---------|--------------|---------|
| HTTPS 443 | All interfaces (or LAN only in Minimal) | Web UI + API |
| HTTP 80 | Redirect to HTTPS | ACME/http-01 if enabled |
| SMB 445 | LAN | File sharing |
| NFS 2049 | LAN optional | Unix clients |
| SSH 22 | Off by default; optional admin | Break-glass |
| WireGuard | UDP user-defined | Remote access |
| Docker published ports | Per-app | App Center only |

**Trust boundary**: Treat the management API as **administrator-equivalent**. LAN clients using SMB are a separate boundary (share ACLs).

## Install-time vs runtime

```mermaid
flowchart TB
  subgraph install [Install time Calamares]
    ISO[Live ISO]
    Part[Partition wizard]
    Seed[Seed config.db]
    Profile[Hardware profile]
    ISO --> Part --> Seed --> Profile
  end

  subgraph runtime [Runtime]
    FB[First-boot wizard]
    NASD[nasd]
    FB --> NASD
    Seed --> NASD
  end

  Part -->|writes| DiskLayout[Disk layout BTRFS or ext4]
  Profile -->|sets| FeatureFlags[feature flags in DB]
```

## Capability detection (runtime)

`nasd` publishes a **capability manifest** used by UI and installer recommendations:

| Capability | Detection | Effect if missing |
|------------|-----------|-------------------|
| `virt.kvm` | CPU flags + `/dev/kvm` | Hide VM manager |
| `ram.zfs` | RAM ≥ 8 GB + user opt-in | Disable ZFS pool creation |
| `cpu.avx` | CPU flags | Warn for ONNX AI module |
| `hw.transcode` | `/dev/dri/renderD*` | Jellyfin software transcode only |
| `docker` | cgroup v2, enough disk | App Center disabled in Minimal |

## Partition layout (default Btrfs install)

| Mount | Subvolume / device | Size guidance |
|-------|-------------------|---------------|
| `/boot/efi` | vfat ESP | 512 MB |
| `/` | `@` subvolume | ≤ 8 GB fixed or thin |
| `/var` | `@var` | grows with logs/docker |
| `/data` | separate subvolume or volume | remainder of system disk or data disks |

Data disks: dedicated btrfs raid or mdadm+LVM PV; **user data never on live ISO**.
