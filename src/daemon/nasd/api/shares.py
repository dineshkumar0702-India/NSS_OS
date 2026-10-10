import json

from fastapi import APIRouter, Depends

from nasd.audit import audit_log
from nasd.core.render import write_samba_config
from nasd.deps import DbDep, require_role
from nasd.errors import Problem
from nasd.models import Share, User, Volume
from nasd.schemas import ShareCreate, SharePublic

router = APIRouter(prefix="/shares", tags=["shares"])


def _share_public(share: Share) -> SharePublic:
    protocols = json.loads(share.protocols)
    return SharePublic(
        id=share.id,
        volume_id=share.volume_id,
        name=share.name,
        protocols=protocols,
    )


@router.get("")
def list_shares(db: DbDep, _user: User = Depends(require_role("viewer"))) -> dict:
    shares = db.query(Share).order_by(Share.name).all()
    return {"items": [_share_public(s) for s in shares]}


@router.post("", response_model=SharePublic)
def create_share(
    body: ShareCreate,
    db: DbDep,
    actor: User = Depends(require_role("operator")),
) -> Share:
    if db.query(Share).filter(Share.name == body.name).first():
        raise Problem(409, "Exists", "share name taken", "VALIDATION_ERROR")
    vol = db.get(Volume, body.volume_id)
    if vol is None:
        raise Problem(404, "Volume missing", "volume not found", "NOT_FOUND")
    share = Share(
        volume_id=body.volume_id,
        name=body.name,
        protocols=json.dumps(body.protocols),
        smb_options_json=json.dumps(body.smb_options),
    )
    db.add(share)
    db.flush()
    write_samba_config(db)
    audit_log(db, actor_user_id=actor.id, action="shares.create", outcome="success", target_id=share.id)
    db.commit()
    db.refresh(share)
    return _share_public(share)
