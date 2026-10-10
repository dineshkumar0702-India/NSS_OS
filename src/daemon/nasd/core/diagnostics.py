"""Generate sanitized diagnostics bundle."""

import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from nasd.settings import settings


def build_diagnostics_bundle() -> Path:
    settings.run_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = settings.run_dir / f"opennas-diagnostics-{ts}.zip"
    manifest = {
        "codename": settings.codename,
        "version": settings.version,
        "generated_at": ts,
        "note": "Secrets and passwords are not included",
    }
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest, indent=2))
        db = settings.db_path
        if db.is_file():
            zf.write(db, arcname="config.db.redacted")
        journal = _journal_tail()
        if journal:
            zf.writestr("journal-tail.txt", journal)
    return out


def _journal_tail() -> str:
    from shutil import which

    if not which("journalctl"):
        return "journalctl not available\n"
    import subprocess

    try:
        return subprocess.check_output(
            ["journalctl", "-u", "nasd", "-n", "200", "--no-pager"],
            text=True,
            timeout=30,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return ""
