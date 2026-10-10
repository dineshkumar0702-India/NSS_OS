#!/usr/bin/env bash
# Smoke-test OpenNAS-Lite ISO in QEMU (BIOS or UEFI).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
ISO="${ISO:-${REPO_ROOT}/build/output/opennas-lite-bookworm-amd64.iso}"
RAM_MB="${RAM_MB:-2048}"
CPUS="${CPUS:-2}"
MODE="${MODE:-bios}"

if [ ! -f "$ISO" ]; then
	echo "ISO not found: $ISO (set ISO= or run build-iso.sh first)" >&2
	exit 1
fi

if ! command -v qemu-system-x86_64 >/dev/null 2>&1; then
	echo "Install qemu-system-x86 (qemu-system-x86_64)" >&2
	exit 1
fi

DISK="${REPO_ROOT}/build/output/qemu-test-disk.img"
qemu-img create -f qcow2 "$DISK" 32G >/dev/null 2>&1 || true

COMMON=(
	-machine type=q35,accel=kvm:tcg
	-m "$RAM_MB"
	-smp "$CPUS"
	-drive "file=${DISK},if=virtio,format=qcow2"
	-cdrom "$ISO"
	-boot d
	-netdev user,id=net0
	-device virtio-net-pci,netdev=net0
	-serial mon:stdio
)

case "$MODE" in
	uefi)
		OVMF_CODE="${OVMF_CODE:-/usr/share/OVMF/OVMF_CODE.fd}"
		OVMF_VARS="${OVMF_VARS:-/usr/share/OVMF/OVMF_VARS.fd}"
		if [ ! -f "$OVMF_CODE" ]; then
			echo "OVMF not found. Install ovmf package or set OVMF_CODE/OVMF_VARS." >&2
			exit 1
		fi
		qemu-system-x86_64 "${COMMON[@]}" \
			-drive if=pflash,format=raw,readonly=on,file="$OVMF_CODE" \
			-drive if=pflash,format=raw,file="$OVMF_VARS"
		;;
	bios|*)
		qemu-system-x86_64 "${COMMON[@]}"
		;;
esac
