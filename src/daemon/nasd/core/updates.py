"""OTA updates with optional Btrfs pre-upgrade snapshot."""

import json
import subprocess
from datetime import datetime, timezone

from nasd.settings import settings


def _utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def apt_update_available() -> dict:
    if not _which("apt-get"):
        return {"simulated": True, "upgradable": 0, "packages": []}
    try:
        subprocess.run(["apt-get", "update"], check=True, capture_output=True, timeout=300)
        out = subprocess.check_output(
            ["apt-get", "-s", "upgrade"],
            text=True,
            timeout=120,
        )
        count = sum(1 for line in out.splitlines() if line.startswith("Inst "))
        return {"simulated": False, "upgradable": count, "preview": out[:4000]}
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        return {"simulated": False, "error": str(exc), "upgradable": 0}


def create_root_snapshot(label: str) -> dict:
    """Create Btrfs snapshot of @ before upgrade. Simulated off-appliance."""
    snap_path = f"/.snapshots/{label}"
    cmd = ["btrfs", "subvolume", "snapshot", "/", snap_path]
    if not settings.allow_system_upgrade:
        return {"status": "simulated", "command": " ".join(cmd), "snapshot": label}
    if not _which("btrfs"):
        return {"status": "skipped", "reason": "btrfs not available"}
    try:
        subprocess.run(cmd, check=True, timeout=600)
        return {"status": "created", "snapshot": label, "path": snap_path}
    except subprocess.CalledProcessError as exc:
        return {"status": "failed", "error": str(exc)}


def run_apt_upgrade() -> dict:
    if not settings.allow_system_upgrade:
        return {"status": "simulated", "command": "apt-get upgrade -y"}
    try:
        subprocess.run(
            ["apt-get", "upgrade", "-y", "--with-new-pkgs"],
            check=True,
            timeout=3600,
        )
        return {"status": "completed", "finished_at": _utcnow()}
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        return {"status": "failed", "error": str(exc)}


def rollback_snapshot(label: str) -> dict:
    cmd = ["btrfs", "subvolume", "delete", "/"]  # placeholder — real rollback needs boot helper
    if not settings.allow_system_upgrade:
        return {
            "status": "simulated",
            "message": f"Would restore snapshot {label} at next maintenance window",
            "warning": "Production rollback uses bootloader + btrfs subvolume default",
        }
    return {"status": "manual_required", "snapshot": label, "note": "Use opennas-rollback helper in Phase 6 packaging"}


def _which(cmd: str) -> bool:
    from shutil import which

    return which(cmd) is not None
