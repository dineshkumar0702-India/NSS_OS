"""Lightweight security posture checks (no external scanners)."""

import json
import subprocess
from pathlib import Path

from sqlalchemy.orm import Session

from nasd.deps import setup_complete
from nasd.models import FeatureFlag, SystemConfig, User
from nasd.settings import settings


def run_advisor(db: Session) -> dict:
    findings: list[dict] = []

    if not setup_complete(db):
        findings.append(
            {
                "id": "setup.incomplete",
                "severity": "high",
                "title": "Initial setup not finished",
                "remediation": "Complete the setup wizard",
            }
        )

    owners = db.query(User).filter(User.role == "owner").count()
    if owners == 0:
        findings.append(
            {
                "id": "auth.no_owner",
                "severity": "critical",
                "title": "No owner account",
                "remediation": "Create an owner user",
            }
        )

    if settings.cookie_secure is False:
        findings.append(
            {
                "id": "https.cookie_insecure",
                "severity": "medium",
                "title": "Session cookies not marked Secure",
                "remediation": "Set NASD_COOKIE_SECURE=true behind HTTPS",
            }
        )

    ssh_enabled = _systemd_active("ssh.service")
    if ssh_enabled == "active":
        findings.append(
            {
                "id": "ssh.enabled",
                "severity": "medium",
                "title": "SSH service is active",
                "remediation": "Disable SSH or restrict to key-based auth and LAN",
            }
        )

    docker = db.get(FeatureFlag, "docker")
    if docker and docker.enabled:
        findings.append(
            {
                "id": "docker.enabled",
                "severity": "low",
                "title": "Docker is enabled",
                "remediation": "Review published container ports and image trust",
            }
        )

    if not Path("/var/lib/nasd/config.db").exists() and settings.data_dir.joinpath("config.db").exists():
        pass

    row = db.get(SystemConfig, "updates.last_apply")
    if row:
        try:
            data = json.loads(row.value_json)
            if data.get("status") == "failed":
                findings.append(
                    {
                        "id": "updates.last_failed",
                        "severity": "high",
                        "title": "Last system update failed",
                        "remediation": "Check logs and consider rollback",
                    }
                )
        except json.JSONDecodeError:
            pass

    score = max(0, 100 - sum(_severity_weight(f["severity"]) for f in findings))
    return {"score": score, "findings": findings}


def _severity_weight(sev: str) -> int:
    return {"critical": 40, "high": 25, "medium": 15, "low": 5}.get(sev, 10)


def _systemd_active(unit: str) -> str:
    if not _which("systemctl"):
        return "unknown"
    try:
        return subprocess.check_output(["systemctl", "is-active", unit], text=True).strip()
    except subprocess.CalledProcessError:
        return "inactive"


def _which(cmd: str) -> bool:
    from shutil import which

    return which(cmd) is not None
