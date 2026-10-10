#!/usr/bin/env bash
# Roll back root filesystem to a Btrfs snapshot created before OTA.
# Usage: opennas-rollback.sh <snapshot_label>
set -euo pipefail
LABEL="${1:?snapshot label required}"
SNAP="/.snapshots/${LABEL}"
if [ ! -d "$SNAP" ]; then
	echo "Snapshot not found: $SNAP" >&2
	exit 1
fi
echo "This will set @$LABEL as default subvolume on next boot."
echo "Run from maintenance mode or initramfs hook in production."
btrfs subvolume set-default "$SNAP" / || true
echo "Set-default issued. Reboot to complete rollback."
