#!/usr/bin/env bash
# Run INSIDE a Debian 12+ VM (VMware / VirtualBox). No WSL and no Windows reboot.
# Mount the Windows project folder first (see docs/BUILD-NO-REBOOT.md).
set -euo pipefail

REPO="${OPENNAS_REPO:-}"
if [ -z "$REPO" ]; then
	for candidate in /mnt/opennas /media/sf_NSS_OS /mnt/hgfs/NSS_OS "$HOME/NSS_OS"; do
		if [ -f "${candidate}/build/scripts/build-iso.sh" ]; then
			REPO="$candidate"
			break
		fi
	done
fi

if [ -z "$REPO" ] || [ ! -f "${REPO}/build/scripts/build-iso.sh" ]; then
	echo "Set OPENNAS_REPO to your NSS_OS path (shared folder mount)." >&2
	echo "Example: export OPENNAS_REPO=/mnt/opennas && bash build/scripts/debian-guest-build.sh" >&2
	exit 1
fi

echo "Building from: $REPO"

export DEBIAN_FRONTEND=noninteractive
sudo apt-get update
sudo apt-get install -y \
	live-build debootstrap squashfs-tools xorriso isolinux syslinux-utils \
	git rsync ca-certificates curl nodejs npm

cd "$REPO"
bash build/scripts/prepare-iso-assets.sh
sudo -E bash build/scripts/build-iso.sh

ISO="${REPO}/build/output/opennas-lite-bookworm-amd64.iso"
if [ -f "$ISO" ]; then
	echo ""
	echo "SUCCESS: $ISO"
	sha256sum "$ISO" | tee "${ISO}.sha256"
	ls -lh "$ISO"
else
	echo "ISO missing after build. See ${REPO}/build/logs/live-build.log" >&2
	exit 1
fi
