# Phase 2 summary — Build system

## What was done

1. **debian-live configuration** — `build/live-build/auto/config` (bookworm amd64, iso-hybrid, GRUB, xz compression, firmware enabled).
2. **Package lists** — `opennas-base.list.chroot`, `opennas-installer.list.chroot` (storage, zram, Calamares/X11 stack, GRUB/shim).
3. **Chroot hooks** — apt/locale setup, size trim, live Calamares autostart, profile seed, `opennas-hw-check`.
4. **Calamares** — `build/calamares/` settings, branding, **opennasprofile** (QML), **opennaspartition** (Python job), standard partition/users/GRUB modules.
5. **Stage script** — `build/scripts/stage-includes.sh` copies Calamares + `config/profiles` + `config.seed.json` into `includes.chroot`.
6. **Build / test scripts** — `build-iso.sh`, `qemu-smoke.sh`, `lint-openapi.sh`.
7. **CI** — `.github/workflows/build-iso.yml` (OpenAPI lint + ISO artifact).
8. **Config seeds** — `config/profiles/{minimal,standard,full}.yaml`, `config/nasd/config.seed.json`.
9. **Metapackage skeleton** — `packaging/opennas-base-meta/` (optional; Calamares `packages.conf` lists concrete packages directly).
10. **Documentation** — [BUILD.md](BUILD.md).

## How to test

See [BUILD.md](BUILD.md). Minimum path:

```bash
sudo bash build/scripts/build-iso.sh
bash build/scripts/qemu-smoke.sh
```

On Windows, use WSL2 or a Debian VM; live-build requires root and Linux.

## What comes next (Phase 3 — wait for `continue`)

1. Implement **`nasd`** (FastAPI): storage planners, users, shares, network, jobs.
2. **`nasctl`** CLI, systemd units, config rendering to Samba/nftables/Caddy.
3. Unit tests and expand OpenAPI to match real endpoints.
4. Calamares **opennaspartition** integration with nasd dry-run API (replace direct `chroot apt` over time).

Reply **`continue`** to start Phase 3.
