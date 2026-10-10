import json
from typing import Any

from sqlalchemy.orm import Session

from nasd.models import AuditEvent, _uuid, _utcnow


def audit_log(
    db: Session,
    *,
    actor_user_id: str | None,
    action: str,
    outcome: str,
    target_type: str | None = None,
    target_id: str | None = None,
    meta: dict[str, Any] | None = None,
) -> None:
    db.add(
        AuditEvent(
            id=_uuid(),
            ts=_utcnow(),
            actor_user_id=actor_user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            outcome=outcome,
            meta_json=json.dumps(meta or {}),
        )
    )
