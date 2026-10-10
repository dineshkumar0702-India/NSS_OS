import json
import time

from fastapi import APIRouter, Depends

from nasd.audit import audit_log
from nasd.core.capabilities import get_capabilities
from nasd.deps import DbDep, get_current_user, require_role, setup_complete
from nasd.errors import Problem
from nasd.models import FeatureFlag, SystemConfig, User, _utcnow
from nasd.schemas import Capabilities, SetupRequest, SystemStatus
from nasd.security import hash_password
from nasd.settings import settings

router = APIRouter(prefix="/system", tags=["system"])
capabilities_router = APIRouter(prefix="/system", tags=["system"])

_START = time.time()


@router.get("/status", response_model=SystemStatus)
def status(db: DbDep) -> SystemStatus:
    complete = setup_complete(db)
    return SystemStatus(
        version=settings.version,
        codename=settings.codename,
        setup_complete=complete,
        uptime_seconds=int(time.time() - _START),
    )


@capabilities_router.get("/capabilities", response_model=Capabilities)
def capabilities(db: DbDep, _user: User = Depends(get_current_user)) -> Capabilities:
    caps = get_capabilities(db)
    return Capabilities(**caps)


@router.post("/setup")
def first_boot_setup(body: SetupRequest, db: DbDep) -> dict:
    if setup_complete(db):
        raise Problem(409, "Already configured", "setup already completed", "VALIDATION_ERROR")
    if db.query(User).count() > 0:
        raise Problem(409, "Users exist", "setup already has users", "VALIDATION_ERROR")

    owner = User(
        username=body.admin_username,
        display_name=body.admin_username,
        role="owner",
        password_hash=hash_password(body.admin_password),
    )
    db.add(owner)
    db.merge(
        SystemConfig(
            key="network.hostname",
            value_json=json.dumps(body.hostname),
            updated_at=_utcnow(),
        )
    )
    db.merge(
        SystemConfig(
            key="timezone",
            value_json=json.dumps(body.timezone),
            updated_at=_utcnow(),
        )
    )
    db.merge(
        SystemConfig(
            key="setup_complete",
            value_json="true",
            updated_at=_utcnow(),
        )
    )
    audit_log(
        db,
        actor_user_id=owner.id,
        action="system.setup",
        outcome="success",
        meta={"hostname": body.hostname},
    )
    db.commit()
    return {"status": "ok", "user": owner.username}
