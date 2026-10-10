import json

from fastapi import APIRouter, Depends

from nasd.audit import audit_log
from nasd.deps import DbDep, require_role
from nasd.models import SystemConfig, User, _utcnow

router = APIRouter(prefix="/vpn", tags=["vpn"])


@router.get("/wireguard")
def get_wireguard(db: DbDep, _user: User = Depends(require_role("admin"))) -> dict:
    row = db.get(SystemConfig, "vpn.wireguard")
    if row is None:
        return {"enabled": False, "peers": [], "interface": {"address": "10.200.0.1/24", "listen_port": 51820}}
    return json.loads(row.value_json)


@router.put("/wireguard")
def put_wireguard(
    body: dict,
    db: DbDep,
    user: User = Depends(require_role("admin")),
) -> dict:
    db.merge(
        SystemConfig(
            key="vpn.wireguard",
            value_json=json.dumps(body),
            updated_at=_utcnow(),
        )
    )
    audit_log(db, actor_user_id=user.id, action="vpn.wireguard.update", outcome="success")
    db.commit()
    return {"status": "saved", "applied": False, "note": "wg-quick sync in Phase 6"}
