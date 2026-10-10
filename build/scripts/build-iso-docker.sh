#!/usr/bin/env bash
# Build OpenNAS-Lite ISO inside Debian bookworm (Docker). Use when WSL/Linux is not on the host.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
IMAGE="${OPENNAS_BUILD_IMAGE:-debian:bookworm}"

if ! command -v docker >/dev/null 2>&1; then
	echo "Docker is required. Install Docker Desktop, then re-run this script." >&2
	exit 1
fi

echo "Building ISO in ${IMAGE} (privileged; 30–90 min)..."
docker run --rm --privileged \
	-v "${REPO_ROOT}:/work" \
	-w /work \
	-e DEBIAN_FRONTEND=noninteractive \
	"${IMAGE}" \
	bash -ec '
		apt-get update
		apt-get install -y live-build debootstrap squashfs-tools xorriso isolinux syslinux-utils \
			git rsync ca-certificates curl
		apt-get install -y nodejs npm 2>/dev/null || true
		bash build/scripts/prepare-iso-assets.sh
		bash build/scripts/build-iso.sh
	'

echo "Done. ISO: ${REPO_ROOT}/build/output/opennas-lite-bookworm-amd64.iso"
