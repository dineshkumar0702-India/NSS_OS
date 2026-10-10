import json
from pathlib import Path

from sqlalchemy.orm import Session

from nasd.models import FeatureFlag, SystemConfig, _utcnow
from nasd.settings import settings


def load_seed_from_files(db: Session) -> None:
    if db.get(SystemConfig, "setup_complete") is not None:
        return

    seed_path = settings.seed_file
    if seed_path.is_file():
        data = json.loads(seed_path.read_text(encoding="utf-8"))
        for key, value in (data.get("system_config") or {}).items():
            db.merge(
                SystemConfig(
                    key=key,
                    value_json=json.dumps(value),
                    updated_at=_utcnow(),
                )
            )
        for name, enabled in (data.get("feature_flags") or {}).items():
            db.merge(
                FeatureFlag(
                    name=name,
                    enabled=1 if enabled else 0,
                    source="profile",
                )
            )
        profile = data.get("opennas_profile")
        if profile:
            db.merge(
                SystemConfig(
                    key="opennas.profile",
                    value_json=json.dumps(profile),
                    updated_at=_utcnow(),
                )
            )
        db.merge(
            SystemConfig(
                key="setup_complete",
                value_json=json.dumps(bool(data.get("setup_complete", False))),
                updated_at=_utcnow(),
            )
        )
        db.commit()
        return

    install = settings.install_profile_file
    if install.is_file():
        profile_data = json.loads(install.read_text(encoding="utf-8"))
        profile = profile_data.get("profile", "standard")
        db.merge(
            SystemConfig(
                key="opennas.profile",
                value_json=json.dumps(profile),
                updated_at=_utcnow(),
            )
        )
        flags = (profile_data.get("profile_data") or {}).get("feature_flags") or {}
        for name, enabled in flags.items():
            db.merge(
                FeatureFlag(name=name, enabled=1 if enabled else 0, source="profile")
            )
        db.merge(
            SystemConfig(
                key="setup_complete",
                value_json="false",
                updated_at=_utcnow(),
            )
        )
        db.commit()
