import json
import shutil
import subprocess
import threading
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from nasd.core.apps_catalog import template_compose_path
from nasd.core import updates as updates_core
from nasd.models import AppInstance, Job, JobLogLine, Pool, SystemConfig, _utcnow
from nasd.settings import settings


def _open_session() -> Session:
    from nasd.database import get_session_factory

    return get_session_factory()()


def _log(db: Session, job_id: str, line: str) -> None:
    db.add(JobLogLine(job_id=job_id, ts=_utcnow(), line=line))


def _finish(job: Job, db: Session, job_id: str, result: dict) -> None:
    job.state = "success"
    job.progress = 100
    job.result_json = json.dumps(result)
    job.finished_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    _log(db, job_id, "completed")
    db.commit()


def _run_pool_create(job_id: str) -> None:
    with _open_session() as db:
        job = db.get(Job, job_id)
        if job is None:
            return
        job.state = "running"
        job.progress = 5
        _log(db, job_id, "pool.create started")
        db.commit()

        payload = json.loads(job.payload_json)
        commands: list[str] = []
        backend = payload.get("backend")
        name = payload.get("name")
        devices = payload.get("devices", [])
        raid_level = payload.get("raid_level")

        if backend == "btrfs":
            raid = raid_level or ("raid1" if len(devices) > 1 else "single")
            commands = [f"mkfs.btrfs -f -d {raid} -L {name} {' '.join(devices)}"]
        elif backend == "mdadm":
            level = raid_level or "1"
            commands = [
                f"mdadm --create /dev/md/{name} --level={level} "
                f"--raid-devices={len(devices)} {' '.join(devices)}"
            ]
        elif backend == "zfs":
            commands = [f"zpool create {name} {' '.join(devices)}"]

        try:
            if settings.allow_storage_mutations:
                for idx, cmd in enumerate(commands):
                    _log(db, job_id, f"exec: {cmd}")
                    db.commit()
                    subprocess.run(cmd, shell=True, check=True, timeout=3600)
                    job.progress = 20 + int(70 * (idx + 1) / max(len(commands), 1))
                    db.commit()
                pool = Pool(
                    name=name,
                    backend=backend,
                    raid_level=raid_level,
                    state="online",
                    metadata_json=json.dumps({"devices": devices}),
                )
                db.add(pool)
                result = {"status": "created", "pool_name": name}
            else:
                _log(db, job_id, "simulated (NASD_ALLOW_STORAGE_MUTATIONS=false)")
                result = {"status": "simulated", "commands": commands}
            _finish(job, db, job_id, result)
        except subprocess.CalledProcessError as exc:
            job.state = "failed"
            job.progress = 100
            job.result_json = json.dumps({"error": str(exc)})
            job.finished_at = _utcnow()
            _log(db, job_id, f"failed: {exc}")
            db.commit()


def _run_snapshot_create(job_id: str) -> None:
    with _open_session() as db:
        job = db.get(Job, job_id)
        if job is None:
            return
        job.state = "running"
        payload = json.loads(job.payload_json)
        cmd = f"btrfs subvolume snapshot {payload.get('name')} ..."
        _log(db, job_id, f"snapshot plan: {cmd}")
        _finish(job, db, job_id, {"status": "simulated", "snapshot_id": payload.get("snapshot_id")})


def _run_backup(job_id: str) -> None:
    with _open_session() as db:
        job = db.get(Job, job_id)
        if job is None:
            return
        job.state = "running"
        payload = json.loads(job.payload_json)
        cmd = [
            "restic",
            "backup",
            payload.get("source_path"),
            "--repo",
            payload.get("target_path"),
        ]
        _log(db, job_id, f"restic: {' '.join(cmd)}")
        if settings.allow_storage_mutations:
            try:
                subprocess.run(cmd, check=True, timeout=7200)
                _finish(job, db, job_id, {"status": "completed"})
            except (subprocess.CalledProcessError, FileNotFoundError) as exc:
                job.state = "failed"
                job.result_json = json.dumps({"error": str(exc)})
                job.finished_at = _utcnow()
                db.commit()
        else:
            _finish(job, db, job_id, {"status": "simulated", "command": cmd})


def _run_app_job(job_id: str) -> None:
    with _open_session() as db:
        job = db.get(Job, job_id)
        if job is None:
            return
        job.state = "running"
        payload = json.loads(job.payload_json)
        instance_id = payload.get("instance_id")
        template_id = payload.get("template_id")
        inst = db.get(AppInstance, instance_id) if instance_id else None
        project = payload.get("compose_project") or (inst.compose_project if inst else None)
        compose_src = template_compose_path(template_id) if template_id else None
        dest = settings.compose_projects_dir / (project or "unknown")
        if compose_src and job.type == "app.install":
            dest.mkdir(parents=True, exist_ok=True)
            shutil.copy2(compose_src, dest / "compose.yaml")
        cmd = ["docker", "compose", "-p", project or "opennas", "up", "-d"]
        if job.type == "app.stop":
            cmd = ["docker", "compose", "-p", project, "stop"]
        elif job.type == "app.uninstall":
            cmd = ["docker", "compose", "-p", project, "down", "-v"]
        _log(db, job_id, f"docker: {' '.join(cmd)}")
        if settings.allow_docker_ops:
            try:
                subprocess.run(cmd, cwd=dest if dest.exists() else None, check=True, timeout=600)
                if inst:
                    inst.state = "running" if job.type in ("app.install", "app.start") else "stopped"
                    if job.type == "app.uninstall":
                        inst.state = "removed"
                _finish(job, db, job_id, {"status": "completed"})
            except (subprocess.CalledProcessError, FileNotFoundError) as exc:
                job.state = "failed"
                job.result_json = json.dumps({"error": str(exc)})
                job.finished_at = _utcnow()
                db.commit()
        else:
            if inst and job.type == "app.install":
                inst.state = "running"
            _finish(job, db, job_id, {"status": "simulated", "command": cmd})


def _run_update_apply(job_id: str) -> None:
    with _open_session() as db:
        job = db.get(Job, job_id)
        if job is None:
            return
        job.state = "running"
        payload = json.loads(job.payload_json)
        label = payload.get("snapshot_label", "pre-ota")
        snap = updates_core.create_root_snapshot(label)
        _log(db, job_id, f"snapshot: {snap}")
        db.merge(
            SystemConfig(
                key="updates.last_snapshot",
                value_json=json.dumps({"label": label, "plan": snap}),
                updated_at=_utcnow(),
            )
        )
        db.commit()
        upgrade = updates_core.run_apt_upgrade()
        _log(db, job_id, f"apt: {upgrade}")
        db.merge(
            SystemConfig(
                key="updates.last_apply",
                value_json=json.dumps(upgrade),
                updated_at=_utcnow(),
            )
        )
        _finish(job, db, job_id, {"snapshot": snap, "upgrade": upgrade})


_HANDLERS = {
    "pool.create": _run_pool_create,
    "snapshot.create": _run_snapshot_create,
    "backup.run": _run_backup,
    "app.install": _run_app_job,
    "app.start": _run_app_job,
    "app.stop": _run_app_job,
    "app.restart": _run_app_job,
    "app.uninstall": _run_app_job,
    "update.apply": _run_update_apply,
}


def _run_job(job_id: str, job_type: str) -> None:
    handler = _HANDLERS.get(job_type)
    if handler:
        handler(job_id)
        return
    with _open_session() as db:
        job = db.get(Job, job_id)
        if job is None:
            return
        job.state = "failed"
        job.result_json = json.dumps({"error": f"unknown job type {job_type}"})
        job.finished_at = _utcnow()
        db.commit()


def enqueue_job(db: Session, job: Job) -> None:
    async_mode = (
        (job.type == "pool.create" and settings.allow_storage_mutations)
        or (job.type.startswith("app.") and settings.allow_docker_ops)
    )
    if async_mode:
        thread = threading.Thread(target=_run_job, args=(job.id, job.type), daemon=True)
        thread.start()
    else:
        _run_job(job.id, job.type)
