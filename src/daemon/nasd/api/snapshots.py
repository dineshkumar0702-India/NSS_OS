import json
import uuid

from fastapi import APIRouter, Depends

from nasd.audit import audit_log
from nasd.core import jobs as job_runner
from nasd.deps import DbDep, require_role
from nasd.errors import Problem
from nasd.models import Job, Snapshot, User, Volume

router = APIRouter(prefix="/storage/snapshots", tags=["storage"])


@router.get("")
def list_snapshots(db: DbDep, _user: User = Depends(require_role("viewer"))) -> dict:
    rows = db.query(Snapshot).order_by(Snapshot.created_at.desc()).limit(100).all()
    return {
        "items": [
            {
                "id": s.id,
                "volume_id": s.volume_id,
                "backend_id": s.backend_id,
                "created_at": s.created_at,
            }
            for s in rows
        ]
    }


@router.post("")
def create_snapshot(
    body: dict,
    db: DbDep,
    user: User = Depends(require_role("admin")),
) -> dict:
    volume_id = body.get("volume_id")
    name = body.get("name") or f"snap-{uuid.uuid4().hex[:8]}"
    if not volume_id:
        raise Problem(400, "Missing volume", "volume_id required", "VALIDATION_ERROR")
    vol = db.get(Volume, volume_id)
    if vol is None:
        raise Problem(404, "Not found", "volume not found", "NOT_FOUND")
    snap = Snapshot(volume_id=volume_id, backend_id=name)
    db.add(snap)
    job = Job(
        type="snapshot.create",
        state="pending",
        payload_json=json.dumps({"volume_id": volume_id, "snapshot_id": snap.id, "name": name}),
    )
    db.add(job)
    audit_log(
        db,
        actor_user_id=user.id,
        action="snapshot.create",
        outcome="success",
        target_id=snap.id,
    )
    db.commit()
    db.refresh(job)
    job_runner.enqueue_job(db, job)
    return {"snapshot_id": snap.id, "job_id": job.id}
