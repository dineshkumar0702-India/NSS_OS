"""Export/import system configuration (non-secret)."""

import json
import hashlib
from sqlalchemy.orm import Session

from nasd.models import BackupPolicy, FeatureFlag, NotificationChannel, Share, SystemConfig, User, _utcnow


def export_bundle(db: Session) -> dict:
    users = [
        {"username": u.username, "role": u.role, "display_name": u.display_name}
        for u in db.query(User).all()
    ]
    shares = [
        {"name": s.name, "volume_id": s.volume_id, "protocols": s.protocols}
        for s in db.query(Share).all()
    ]
    flags = {f.name: bool(f.enabled) for f in db.query(FeatureFlag).all()}
    policies = [
        {
            "name": p.name,
            "source_path": p.source_path,
            "target_path": p.target_path,
            "schedule_cron": p.schedule_cron,
        }
        for p in db.query(BackupPolicy).all()
    ]
    channels = [
        {"type": c.type, "name": c.name, "enabled": bool(c.enabled)}
        for c in db.query(NotificationChannel).all()
    ]
    sys_rows = {}
    for r in db.query(SystemConfig).all():
        if r.key.startswith("secret."):
            continue
        try:
            sys_rows[r.key] = json.loads(r.value_json)
        except json.JSONDecodeError:
            sys_rows[r.key] = r.value_json
    body = {
        "schema_version": 1,
        "exported_at": _utcnow(),
        "users": users,
        "shares": shares,
        "feature_flags": flags,
        "backup_policies": policies,
        "notification_channels": channels,
        "system_config": sys_rows,
    }
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
    body["signature"] = hashlib.sha256(canonical.encode()).hexdigest()
    return body


def import_bundle(db: Session, data: dict, merge: bool = True) -> dict:
    if data.get("schema_version") != 1:
        raise ValueError("unsupported schema_version")
    imported = {"feature_flags": 0, "system_config": 0}
    for name, enabled in (data.get("feature_flags") or {}).items():
        db.merge(FeatureFlag(name=name, enabled=1 if enabled else 0, source="import"))
        imported["feature_flags"] += 1
    for key, value in (data.get("system_config") or {}).items():
        if key in ("setup_complete", "schema_version"):
            continue
        db.merge(
            SystemConfig(
                key=key,
                value_json=json.dumps(value),
                updated_at=_utcnow(),
            )
        )
        imported["system_config"] += 1
    db.commit()
    return {"status": "ok", "imported": imported, "merge": merge}
