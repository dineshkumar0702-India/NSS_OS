# OpenNAS-Lite — Administrator guide

This guide is for operators managing an installed appliance: storage, shares, users, apps, updates, and safety controls. The web UI is **English-only** in current releases.

## Access and roles

| Interface | URL / path | Notes |
|-----------|------------|--------|
| Web UI | `https://<hostname-or-ip>/` | Served by **Caddy**; API proxied to `nasd` |
| API | `http://127.0.0.1:8741/api/v1/` | Loopback only; use Caddy or SSH tunnel remotely |
| CLI | `nasctl` | Same API; set `NASD_URL` if needed |

**Authentication:** Browser sessions use an HTTP-only cookie (`nas_session` by default). Admin actions that change disks, run upgrades, or start destructive jobs require **dry-run** plus a **confirm token** returned from the dry-run response.

**nasctl examples:**

```bash
export NASD_URL=http://127.0.0.1:8741
nasctl status
nasctl capabilities
nasctl disks
nasctl updates
nasctl advisor
nasctl login admin 'your-password'
```

Optional API token: `~/.config/nasctl/credentials` with `token=...` or `NASD_TOKEN` in the environment (when token auth is enabled in your build).

## Dashboard

The dashboard summarizes system health, service state, and quick links. Use it after install to confirm **nasd**, **Caddy**, **Samba**, and network services are running.

## Storage

**Disks:** Lists block devices seen by the host. Verify serial/size before any operation.

**Pools:** Btrfs-oriented pool workflows (with simulation when mutations are disabled).

1. Open **Storage** → create or extend a pool.
2. Submit with **`dry_run: true`** (default in API; UI mirrors this).
3. Review the planned commands, subvolumes, and devices.
4. Submit again with the **`confirm_token`** from the dry-run response.

**Production flag:** On a real appliance, operators enable mutations only after backup and maintenance window:

```bash
# /etc/systemd/system/nasd.service.d/override.conf (example)
[Service]
Environment=NASD_ALLOW_STORAGE_MUTATIONS=true
```

Then `systemctl daemon-reload && systemctl restart nasd`.

**Risks:** Wrong disk selection causes **permanent data loss**. Mixed-size BTRFS RAID has capacity and balance quirks — see [HARDWARE.md](HARDWARE.md).

## Snapshots

**Snapshots** (Btrfs subvolume snapshots) are created via the API/UI with job tracking. Use before major upgrades or bulk deletes. Snapshot jobs respect the same safety posture as storage when mutations are off (simulated).

## Shares (SMB)

1. Ensure a pool/path exists and permissions are set on the filesystem.
2. **Shares** → create share → set name, path, guest access, and ACLs.
3. `nasd` renders Samba configuration to `/etc/samba/smb.conf` (path configurable).

Restart or reload Samba as prompted by the UI or:

```bash
sudo systemctl reload smbd nmbd
```

## Users

Manage local NAS users for SMB and UI access. Password changes invalidate existing sessions per security model. Export/import of configuration **does not** include password hashes — re-set passwords after import.

## Files

The **Files** browser lists paths allowed by server-side roots (not a full arbitrary filesystem browser). Use SMB for heavy client workloads.

## Network

Configure interfaces, static/DHCP, and hostname. Misconfiguration can lock you out — keep console or IPMI access available.

## Firewall and security

- **nftables** is the default firewall backend; rules file path: `/etc/nftables.conf`.
- **Security advisor** (`GET /api/v1/security/advisor` or **Security** page) returns a score and findings (HTTPS cookies, open ports, etc.).
- **fail2ban** may be enabled on Standard/Full profiles.

Remediation items often reference:

- `NASD_COOKIE_SECURE=true` when serving the UI over HTTPS
- Closing WAN-facing management ports

See [architecture/security-model.md](architecture/security-model.md) for the full threat model.

## Services

Enable or disable systemd units exposed through the API (Avahi, Docker, etc.) according to install profile and RAM.

## App Center

Curated Compose templates live under `/usr/share/opennas/apps` (or `NASD_APPS_DIR` in development).

1. **Apps** → catalog → install instance.
2. Lifecycle actions (start/stop) run as jobs.

**Docker flag (production):**

```bash
Environment=NASD_ALLOW_DOCKER_OPS=true
```

Without it, install/start actions are **simulated** for safety in dev/lab images.

Bundled examples: Jellyfin, Pi-hole — see `apps/` in the repository.

## Backups

- Define **policies** (schedule, retention, paths).
- **Run** triggers a `backup.run` job (restic-oriented).
- Store repository credentials securely; test restore on a non-production copy regularly.

## VPN (WireGuard)

**VPN** page edits WireGuard configuration stored by `nasd`. Applying keys to the running interface may require additional host integration in your build — treat exported configs as sensitive.

## Notifications

Configure channels (email/webhook placeholders per implementation). Verify delivery after changing SMTP or firewall rules.

## Virtual machines

The **VM** API is a stub for KVM/libvirt integration. Do not rely on it for production workloads until your release notes say otherwise.

## Updates (OTA)

1. **Updates** → view status.
2. **Check** for available packages.
3. **Apply** with **dry-run** first — review snapshot plan and apt changes.
4. Confirm with token to enqueue `update.apply`.

**Production upgrades:**

```bash
Environment=NASD_ALLOW_SYSTEM_UPGRADE=true
```

Default is **false**: snapshot and `apt upgrade` steps are **logged/simulated**.

**Rollback:** API `POST /updates/rollback` and host script `packaging/scripts/opennas-rollback.sh` (Btrfs default subvolume — verify on your root layout before relying on it).

Always have backups and a console session before applying updates on production data.

## Configuration export and import

- **Export:** `GET /api/v1/system/config/export` — JSON bundle without password hashes.
- **Import:** `POST /api/v1/system/config/import` — merges settings; review diff in UI when available.

Use exports for DR documentation and staging clones, not as a secret store.

## Diagnostics bundle

`POST /api/v1/system/diagnostics/bundle` creates a ZIP under `/run/nasd/` containing logs and sanitized configuration for support. Download promptly; `/run` may be tmpfs and cleared on reboot.

## Jobs

Long-running work (storage, backups, apps, updates) appears under **Jobs** (API `/api/v1/jobs`). Poll status or use the UI job panel. Failed jobs retain log lines in the database for audit.

## Environment reference (`nasd`)

| Variable | Default | Meaning |
|----------|---------|---------|
| `NASD_DATA_DIR` | `/var/lib/nasd` | SQLite DB, keys, compose state |
| `NASD_ALLOW_STORAGE_MUTATIONS` | `false` | Real disk/pool operations |
| `NASD_ALLOW_DOCKER_OPS` | `false` | Real Docker Compose actions |
| `NASD_ALLOW_SYSTEM_UPGRADE` | `false` | Real apt upgrade / snapshot |
| `NASD_COOKIE_SECURE` | `true` | Secure session cookies (use with HTTPS) |
| `NASD_APPS_DIR` | `/usr/share/opennas/apps` | App Center templates |

Full settings: `src/daemon/nasd/settings.py`.

## Maintenance windows

Recommended order:

1. Notify users; pause backup jobs if needed.
2. Snapshot critical volumes.
3. Export config bundle.
4. Dry-run update or storage change → confirm.
5. Verify services and advisor score.

## Further reading

- [INSTALL.md](INSTALL.md) — install and first boot
- [TESTING.md](TESTING.md) — QEMU matrix and manual RAID/OTA tests
- [BUILD.md](BUILD.md) — ISO rebuild after config changes
- [DEVELOPER.md](DEVELOPER.md) — API and development workflow
