import json
import re
import subprocess
from pathlib import Path

from sqlalchemy.orm import Session

from nasd.models import FeatureFlag, SystemConfig


def _ram_mb() -> int:
    try:
        text = Path("/proc/meminfo").read_text(encoding="utf-8")
        for line in text.splitlines():
            if line.startswith("MemTotal:"):
                return int(line.split()[1]) // 1024
    except OSError:
        pass
    return 0


def _has_virt() -> bool:
    try:
        cpu = Path("/proc/cpuinfo").read_text(encoding="utf-8")
        if not re.search(r"\b(vmx|svm)\b", cpu):
            return False
        return Path("/dev/kvm").exists()
    except OSError:
        return False


def _flag(db: Session, name: str) -> bool:
    row = db.get(FeatureFlag, name)
    return bool(row and row.enabled)


def get_capabilities(db: Session) -> dict:
    profile_row = db.get(SystemConfig, "opennas.profile")
    profile = "standard"
    if profile_row:
        try:
            profile = json.loads(profile_row.value_json)
        except json.JSONDecodeError:
            profile = profile_row.value_json.strip('"')

    ram = _ram_mb()
    zfs_cap = _flag(db, "zfs") and ram >= 8192
    return {
        "profile": profile,
        "ram_mb": ram,
        "docker": _flag(db, "docker"),
        "zfs": zfs_cap,
        "virtualization": _flag(db, "virtualization") and _has_virt(),
        "ai_photos": _flag(db, "ai_photos"),
    }


def recommend_profile() -> str:
    ram = _ram_mb()
    if ram < 3500:
        return "minimal"
    if ram < 7500:
        return "standard"
    return "full"
