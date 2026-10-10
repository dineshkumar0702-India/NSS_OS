#!/usr/bin/env bash
# QEMU acceptance matrix helper (run on Linux with qemu-system-x86_64).
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
ISO="${ISO:-${REPO_ROOT}/build/output/opennas-lite-bookworm-amd64.iso}"
RAM_MB="${RAM_MB:-2048}"
CPUS="${CPUS:-2}"

if [ ! -f "$ISO" ]; then
	echo "ISO missing: $ISO" >&2
	exit 1
fi

echo "=== Matrix: BIOS boot ==="
MODE=bios bash "${REPO_ROOT}/build/scripts/qemu-smoke.sh" || true

echo "=== Matrix: UEFI boot ==="
MODE=uefi bash "${REPO_ROOT}/build/scripts/qemu-smoke.sh" || true

echo "=== Matrix: low-RAM profile (2048 MiB) ==="
RAM_MB=2048 CPUS=2 bash "${REPO_ROOT}/build/scripts/qemu-benchmark.sh" || true

cat <<'EOF'

Manual checks (record pass/fail):
- [ ] Calamares completes on empty 32G disk
- [ ] Installed system boots GRUB BIOS + UEFI
- [ ] Web UI setup + login on LAN
- [ ] Storage dry-run shows confirm_token (no mkfs without flag)
- [ ] 1-disk, 2-disk, 12-disk layouts (virtio disks) — partition wizard
- [ ] Simulated RAID degrade/rebuild documented in TESTING.md

EOF
