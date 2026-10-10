import json
import re

from fastapi import APIRouter, Depends

from nasd.audit import audit_log
from nasd.core import jobs as job_runner
from nasd.core.apps_catalog import discover_catalog, get_template
from nasd.core.capabilities import get_capabilities
from nasd.deps import DbDep, require_role
from nasd.errors import Problem
from nasd.models import AppInstance, Job, User
router = APIRouter(prefix="/apps", tags=["apps"])


@router.get("/catalog")
def catalog(db: DbDep, _user: User = Depends(require_role("viewer"))) -> dict:
    caps = get_capabilities(db)
    items = []
    for tpl in discover_catalog():
        min_profile = tpl.get("min_profile", "standard")
        if min_profile == "full" and not caps.get("docker"):
            continue
        items.append(tpl)
    return {"items": items}


@router.get("/instances")
def list_instances(db: DbDep, _user: User = Depends(require_role("viewer"))) -> dict:
    rows = db.query(AppInstance).order_by(AppInstance.compose_project).all()
    return {
        "items": [
            {
                "id": a.id,
                "template_id": a.template_id,
                "state": a.state,
                "compose_project": a.compose_project,
            }
            for a in rows
        ]
    }


@router.post("/instances")
def install_app(
    body: dict,
    db: DbDep,
    user: User = Depends(require_role("operator")),
) -> dict:
    caps = get_capabilities(db)
    if not caps.get("docker"):
        raise Problem(403, "Docker disabled", "enable Docker profile first", "CAPABILITY_DENIED")
    template_id = body.get("template_id")
    tpl = get_template(template_id) if template_id else None
    if tpl is None:
        raise Problem(404, "Not found", "unknown template", "NOT_FOUND")
    name = body.get("name") or template_id
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", name):
        raise Problem(400, "Invalid name", "invalid instance name", "VALIDATION_ERROR")
    instance = AppInstance(
        template_id=template_id,
        state="installing",
        compose_project=f"opennas-{name}",
        resource_limits_json=json.dumps(body.get("resource_limits") or {}),
    )
    db.add(instance)
    job = Job(
        type="app.install",
        state="pending",
        payload_json=json.dumps({"instance_id": instance.id, "template_id": template_id}),
    )
    db.add(job)
    audit_log(db, actor_user_id=user.id, action="app.install", outcome="success", target_id=instance.id)
    db.commit()
    db.refresh(instance)
    db.refresh(job)
    job_runner.enqueue_job(db, job)
    return {"instance_id": instance.id, "job_id": job.id}


@router.post("/instances/{instance_id}/action")
def app_action(
    instance_id: str,
    body: dict,
    db: DbDep,
    user: User = Depends(require_role("operator")),
) -> dict:
    action = body.get("action")
    if action not in ("start", "stop", "restart", "uninstall"):
        raise Problem(400, "Invalid action", "unsupported action", "VALIDATION_ERROR")
    inst = db.get(AppInstance, instance_id)
    if inst is None:
        raise Problem(404, "Not found", "instance not found", "NOT_FOUND")
    job = Job(
        type=f"app.{action}",
        state="pending",
        payload_json=json.dumps({"instance_id": instance_id, "compose_project": inst.compose_project}),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    job_runner.enqueue_job(db, job)
    return {"job_id": job.id}
