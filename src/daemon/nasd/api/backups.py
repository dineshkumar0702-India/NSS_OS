import json

from fastapi import APIRouter, Depends

from nasd.audit import audit_log
from nasd.core import jobs as job_runner
from nasd.deps import DbDep, require_role
from nasd.errors import Problem
from nasd.models import BackupPolicy, Job, User

router = APIRouter(prefix="/backups", tags=["backups"])


@router.get("/policies")
def list_policies(db: DbDep, _user: User = Depends(require_role("viewer"))) -> dict:
    rows = db.query(BackupPolicy).order_by(BackupPolicy.name).all()
    return {
        "items": [
            {
                "id": p.id,
                "name": p.name,
                "source_path": p.source_path,
                "target_path": p.target_path,
                "schedule_cron": p.schedule_cron,
                "enabled": bool(p.enabled),
            }
            for p in rows
        ]
    }


@router.post("/policies")
def create_policy(
    body: dict,
    db: DbDep,
    user: User = Depends(require_role("operator")),
) -> dict:
    policy = BackupPolicy(
        name=body["name"],
        source_path=body["source_path"],
        target_path=body["target_path"],
        schedule_cron=body.get("schedule_cron"),
        enabled=1 if body.get("enabled", True) else 0,
        config_json=json.dumps(body.get("config") or {}),
    )
    db.add(policy)
    audit_log(db, actor_user_id=user.id, action="backup.policy.create", outcome="success", target_id=policy.id)
    db.commit()
    db.refresh(policy)
    return {"id": policy.id}


@router.post("/run")
def run_backup(
    body: dict,
    db: DbDep,
    user: User = Depends(require_role("operator")),
) -> dict:
    policy_id = body.get("policy_id")
    policy = db.get(BackupPolicy, policy_id) if policy_id else None
    payload = {
        "policy_id": policy_id,
        "source_path": body.get("source_path") or (policy.source_path if policy else None),
        "target_path": body.get("target_path") or (policy.target_path if policy else None),
    }
    if not payload["source_path"] or not payload["target_path"]:
        raise Problem(400, "Invalid", "source_path and target_path required", "VALIDATION_ERROR")
    job = Job(type="backup.run", state="pending", payload_json=json.dumps(payload))
    db.add(job)
    audit_log(db, actor_user_id=user.id, action="backup.run", outcome="success", target_id=job.id)
    db.commit()
    db.refresh(job)
    job_runner.enqueue_job(db, job)
    return {"job_id": job.id}
