#!/usr/bin/env bash
# Build OpenNAS-Lite hybrid ISO (BIOS + UEFI) using debian live-build.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
LB_DIR="${REPO_ROOT}/build/live-build"
OUT_DIR="${REPO_ROOT}/build/output"
LOG_DIR="${REPO_ROOT}/build/logs"

require_root() {
	if [ "$(id -u)" -ne 0 ]; then
		echo "Re-run as root: sudo $0" >&2
		exit 1
	fi
}

check_deps() {
	local missing=0
	for cmd in lb debootstrap mksquashfs xorriso; do
		if ! command -v "$cmd" >/dev/null 2>&1; then
			echo "Missing dependency: $cmd (install live-build debootstrap squashfs-tools xorriso)" >&2
			missing=1
		fi
	done
	if [ "$missing" -ne 0 ]; then
		exit 1
	fi
}

main() {
	require_root
	check_deps

	mkdir -p "${OUT_DIR}" "${LOG_DIR}"
	bash "${REPO_ROOT}/build/scripts/prepare-iso-assets.sh"

	cd "${LB_DIR}"
	chmod +x auto/config 2>/dev/null || true
	find config/hooks -name '*.hook*' -exec chmod +x {} + 2>/dev/null || true

	if [ -d config ]; then
		./auto/config
	fi

	echo "Starting live-build (this may take 30-90 minutes)..."
	lb build 2>&1 | tee "${LOG_DIR}/live-build.log"

	ISO_SRC=""
	for candidate in \
		"${LB_DIR}/live-image-amd64.hybrid.iso" \
		"${LB_DIR}/binary/live-image-amd64.hybrid.iso" \
		"${LB_DIR}/binary.hybrid.iso"; do
		if [ -f "$candidate" ]; then
			ISO_SRC="$candidate"
			break
		fi
	done

	if [ -z "$ISO_SRC" ]; then
		echo "Build finished but ISO not found. See ${LOG_DIR}/live-build.log" >&2
		exit 1
	fi

	DEST="${OUT_DIR}/opennas-lite-${BUILD_VERSION:-bookworm}-amd64.iso"
	cp -f "$ISO_SRC" "$DEST"
	sha256sum "$DEST" | tee "${DEST}.sha256"

	SIZE_MB=$(( $(stat -c%s "$DEST" 2>/dev/null || stat -f%z "$DEST") / 1024 / 1024 ))
	echo "ISO: ${DEST} (${SIZE_MB} MiB)"
	if [ "$SIZE_MB" -gt 1536 ]; then
		echo "WARNING: ISO exceeds 1.5 GB budget (${SIZE_MB} MiB). Trim package lists or hooks." >&2
	fi
}

main "$@"
