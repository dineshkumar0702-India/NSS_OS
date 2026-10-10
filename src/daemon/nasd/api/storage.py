import json

from fastapi import APIRouter, Depends

from nasd.audit import audit_log
from nasd.core import jobs as job_runner
from nasd.core.disks import list_block_devices
from nasd.core.storage import execute_pool_create, list_pools, plan_pool_create
from nasd.deps import DbDep, require_role
from nasd.models import Job, User
from nasd.schemas import Disk, PoolCreateRequest, PoolPublic

router = APIRouter(prefix="/storage", tags=["storage"])


@router.get("/disks")
def storage_disks(
    db: DbDep,
    _user: User = Depends(require_role("viewer")),
) -> dict:
    return {"items": [Disk(**d) for d in list_block_devices()]}


@router.get("/pools")
def storage_pools(
    db: DbDep,
    _user: User = Depends(require_role("viewer")),
) -> dict:
    pools = list_pools(db)
    return {
        "items": [
            PoolPublic(
                id=p.id,
                name=p.name,
                backend=p.backend,
                raid_level=p.raid_level,
                state=p.state,
            )
            for p in pools
        ]
    }


@router.post("/pools")
def storage_create_pool(
    body: PoolCreateRequest,
    db: DbDep,
    user: User = Depends(require_role("admin")),
):
    if body.dry_run or not body.confirm_token:
        plan = plan_pool_create(
            db,
            name=body.name,
            backend=body.backend,
            devices=body.devices,
            raid_level=body.raid_level,
        )
        audit_log(
            db,
            actor_user_id=user.id,
            action="storage.pool.plan",
            outcome="success",
            target_type="pool",
            target_id=body.name,
        )
        db.commit()
        return plan

    job = execute_pool_create(
        db,
        name=body.name,
        backend=body.backend,
        devices=body.devices,
        raid_level=body.raid_level,
        confirm_token=body.confirm_token,
    )
    audit_log(
        db,
        actor_user_id=user.id,
        action="storage.pool.create",
        outcome="success",
        target_type="job",
        target_id=job.id,
    )
    db.commit()
    job_runner.enqueue_job(db, job)
    db.commit()
    return {"job_id": job.id}


@router.get("/pools/{pool_id}")
def storage_get_pool(
    pool_id: str,
    db: DbDep,
    _user: User = Depends(require_role("viewer")),
):
    from nasd.models import Pool

    pool = db.get(Pool, pool_id)
    if pool is None:
        from nasd.errors import Problem

        raise Problem(404, "Not found", "pool not found", "NOT_FOUND")
    return PoolPublic(
        id=pool.id,
        name=pool.name,
        backend=pool.backend,
        raid_level=pool.raid_level,
        state=pool.state,
    )
