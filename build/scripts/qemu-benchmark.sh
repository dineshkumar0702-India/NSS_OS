#!/usr/bin/env bash
# Boot-time smoke benchmark for old-hardware profile (2 vCPU / 2 GB RAM).
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
ISO="${ISO:-${REPO_ROOT}/build/output/opennas-lite-bookworm-amd64.iso}"
RAM_MB="${RAM_MB:-2048}"
CPUS="${CPUS:-2}"
DISK="${REPO_ROOT}/build/output/qemu-bench.qcow2"

if [ ! -f "$ISO" ]; then
	echo "ISO not found: $ISO" >&2
	exit 1
fi

qemu-img create -f qcow2 "$DISK" 32G 2>/dev/null || true

START=$(date +%s)
echo "Starting QEMU (target: cold boot to installer/live < 60s on HDD-class; SSD faster)"
echo "RAM=${RAM_MB}MiB CPUs=${CPUS}"

timeout 120 qemu-system-x86_64 \
	-m "$RAM_MB" -smp "$CPUS" \
	-drive "file=${DISK},if=virtio,format=qcow2" \
	-cdrom "$ISO" -boot d \
	-netdev user,id=n0 -device virtio-net-pci,netdev=n0 \
	-display none -serial stdio \
	2>/dev/null || true

END=$(date +%s)
echo "Elapsed: $((END - START))s (manual: measure time-to-web-UI separately with nasd running)"
