import json

from fastapi import APIRouter, Depends

from nasd.deps import DbDep, require_role
from nasd.errors import Problem
from nasd.models import Job, JobLogLine, User
from nasd.schemas import JobPublic

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("")
def list_jobs(db: DbDep, _user: User = Depends(require_role("viewer"))) -> dict:
    jobs = db.query(Job).order_by(Job.created_at.desc()).limit(50).all()
    return {"items": [_job_public(db, j) for j in jobs]}


@router.get("/{job_id}")
def get_job(job_id: str, db: DbDep, _user: User = Depends(require_role("viewer"))) -> dict:
    job = db.get(Job, job_id)
    if job is None:
        raise Problem(404, "Not found", "job not found", "NOT_FOUND")
    logs = (
        db.query(JobLogLine)
        .filter(JobLogLine.job_id == job_id)
        .order_by(JobLogLine.id.desc())
        .limit(50)
        .all()
    )
    return {
        "job": _job_public(db, job),
        "logs": [{"ts": l.ts, "line": l.line} for l in reversed(logs)],
        "result": json.loads(job.result_json or "{}"),
    }


def _job_public(db: DbDep, job: Job) -> JobPublic:
    last = (
        db.query(JobLogLine)
        .filter(JobLogLine.job_id == job.id)
        .order_by(JobLogLine.id.desc())
        .first()
    )
    return JobPublic(
        id=job.id,
        type=job.type,
        state=job.state,
        progress=job.progress,
        message=last.line if last else None,
    )
