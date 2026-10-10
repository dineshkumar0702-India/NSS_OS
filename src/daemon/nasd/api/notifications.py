import json

from fastapi import APIRouter, Depends

from nasd.audit import audit_log
from nasd.deps import DbDep, require_role
from nasd.models import NotificationChannel, User

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/channels")
def list_channels(db: DbDep, _user: User = Depends(require_role("admin"))) -> dict:
    rows = db.query(NotificationChannel).order_by(NotificationChannel.name).all()
    return {
        "items": [
            {
                "id": c.id,
                "type": c.type,
                "name": c.name,
                "enabled": bool(c.enabled),
                "config": json.loads(c.config_json or "{}"),
            }
            for c in rows
        ]
    }


@router.put("/channels")
def upsert_channels(
    body: dict,
    db: DbDep,
    user: User = Depends(require_role("admin")),
) -> dict:
    items = body.get("items") or []
    for item in items:
        cid = item.get("id")
        if cid:
            row = db.get(NotificationChannel, cid)
            if row:
                row.type = item.get("type", row.type)
                row.name = item.get("name", row.name)
                row.enabled = 1 if item.get("enabled", True) else 0
                row.config_json = json.dumps(item.get("config") or {})
                continue
        db.add(
            NotificationChannel(
                type=item["type"],
                name=item["name"],
                enabled=1 if item.get("enabled", True) else 0,
                config_json=json.dumps(item.get("config") or {}),
            )
        )
    audit_log(db, actor_user_id=user.id, action="notifications.update", outcome="success")
    db.commit()
    return {"status": "ok"}
