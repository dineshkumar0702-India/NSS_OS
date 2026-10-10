import json
import secrets
import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from nasd.audit import audit_log
from nasd.core import jobs as job_runner
from nasd.core import updates as updates_core
from nasd.core.config_bundle import export_bundle, import_bundle
from nasd.core.diagnostics import build_diagnostics_bundle
from nasd.core.security_advisor import run_advisor
from nasd.core.storage import _confirm_expiry, _payload_hash
from nasd.deps import DbDep, require_role
from nasd.errors import Problem
from nasd.models import ConfirmToken, Job, SystemConfig, User, _utcnow

router = APIRouter(tags=["system"])


@router.get("/updates/status")
def updates_status(db: DbDep, _user: User = Depends(require_role("viewer"))) -> dict:
    last = db.get(SystemConfig, "updates.last_apply")
    snap = db.get(SystemConfig, "updates.last_snapshot")
    last_data = json.loads(last.value_json) if last else {}
    snap_data = json.loads(snap.value_json) if snap else {}
    return {
        "last_apply": last_data,
        "last_snapshot": snap_data,
        "check": updates_core.apt_update_available(),
    }


@router.post("/updates/check")
def updates_check(_user: User = Depends(require_role("admin"))) -> dict:
    return updates_core.apt_update_available()


@router.post("/updates/apply")
def updates_apply(
    body: dict,
    db: DbDep,
    user: User = Depends(require_role("admin")),
):
    label = body.get("snapshot_label") or f"pre-ota-{uuid.uuid4().hex[:8]}"
    payload = {"snapshot_label": label}
    if body.get("dry_run") or not body.get("confirm_token"):
        token = secrets.token_urlsafe(24)
        db.add(
            ConfirmToken(
                token=token,
                operation="updates.apply",
                payload_hash=_payload_hash(payload),
                expires_at=_confirm_expiry(),
            )
        )
        preview = updates_core.create_root_snapshot(label)
        db.commit()
        return {
            "confirm_token": token,
            "snapshot_label": label,
            "snapshot_plan": preview,
            "apt_preview": updates_core.apt_update_available(),
        }
    row = db.get(ConfirmToken, body["confirm_token"])
    if row is None or row.operation != "updates.apply":
        raise Problem(400, "Invalid token", "confirm_token invalid", "CONFIRMATION_REQUIRED")
    if row.payload_hash != _payload_hash(payload):
        raise Problem(400, "Token mismatch", "snapshot_label mismatch", "CONFIRMATION_REQUIRED")
    job = Job(type="update.apply", state="pending", payload_json=json.dumps(payload))
    db.delete(row)
    db.add(job)
    audit_log(db, actor_user_id=user.id, action="updates.apply", outcome="success", target_id=job.id)
    db.commit()
    db.refresh(job)
    job_runner.enqueue_job(db, job)
    return {"job_id": job.id}


@router.post("/updates/rollback")
def updates_rollback(
    body: dict,
    db: DbDep,
    user: User = Depends(require_role("admin")),
) -> dict:
    snap_row = db.get(SystemConfig, "updates.last_snapshot")
    label = body.get("snapshot_label")
    if not label and snap_row:
        label = json.loads(snap_row.value_json).get("label")
    if not label:
        raise Problem(400, "No snapshot", "snapshot_label required", "VALIDATION_ERROR")
    result = updates_core.rollback_snapshot(label)
    audit_log(db, actor_user_id=user.id, action="updates.rollback", outcome="success", meta=result)
    db.commit()
    return result


@router.get("/security/advisor")
def security_advisor(db: DbDep, _user: User = Depends(require_role("admin"))) -> dict:
    return run_advisor(db)


@router.get("/system/config/export")
def config_export(db: DbDep, _user: User = Depends(require_role("admin"))) -> dict:
    return export_bundle(db)


@router.post("/system/config/import")
def config_import(
    body: dict,
    db: DbDep,
    user: User = Depends(require_role("admin")),
) -> dict:
    try:
        result = import_bundle(db, body, merge=body.get("merge", True))
    except ValueError as exc:
        raise Problem(400, "Import failed", str(exc), "VALIDATION_ERROR")
    audit_log(db, actor_user_id=user.id, action="config.import", outcome="success")
    return result


@router.post("/system/diagnostics/bundle")
def diagnostics_bundle(
    db: DbDep,
    user: User = Depends(require_role("admin")),
):
    path = build_diagnostics_bundle()
    audit_log(db, actor_user_id=user.id, action="diagnostics.bundle", outcome="success")
    db.commit()
    return FileResponse(path, filename=path.name, media_type="application/zip")
