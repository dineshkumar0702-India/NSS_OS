import hashlib
import json
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from nasd.core.disks import device_exists, list_block_devices
from nasd.errors import Problem
from nasd.models import ConfirmToken, Job, Pool, _utcnow
from nasd.settings import settings


def _payload_hash(payload: dict) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(body.encode()).hexdigest()


def _confirm_expiry(minutes: int = 15) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    return exp.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def plan_pool_create(
    db: Session,
    *,
    name: str,
    backend: str,
    devices: list[str],
    raid_level: str | None,
) -> dict:
    if backend not in ("btrfs", "mdadm", "zfs"):
        raise Problem(400, "Invalid backend", "backend must be btrfs, mdadm, or zfs", "VALIDATION_ERROR")
    if not name or not name.replace("-", "").replace("_", "").isalnum():
        raise Problem(400, "Invalid name", "pool name must be alphanumeric with - or _", "VALIDATION_ERROR")
    if db.query(Pool).filter(Pool.name == name).first():
        raise Problem(409, "Pool exists", f"Pool '{name}' already exists", "VALIDATION_ERROR")
    if len(devices) < 1:
        raise Problem(400, "No devices", "at least one device required", "VALIDATION_ERROR")

    warnings: list[str] = []
    commands: list[str] = []
    known = {d["path"] for d in list_block_devices()}
    for dev in devices:
        if not device_exists(dev):
            raise Problem(400, "Device missing", f"{dev} not found", "VALIDATION_ERROR")
        if dev not in known and settings.allow_storage_mutations:
            warnings.append(f"{dev} not listed in discovery cache")

    if backend == "btrfs":
        raid = raid_level or "raid1" if len(devices) > 1 else "single"
        if raid in ("raid5", "raid6"):
            warnings.append("btrfs raid5/6 has parity risks; prefer raid1/raid10 for critical data")
        devs = " ".join(devices)
        commands.append(f"mkfs.btrfs -f -d {raid} -L {name} {devs}")
        commands.append(f"btrfs subvolume create /mnt/{name}/@data")
    elif backend == "mdadm":
        level = raid_level or "1"
        commands.append(f"mdadm --create /dev/md/{name} --level={level} --raid-devices={len(devices)} {' '.join(devices)}")
    elif backend == "zfs":
        if not settings.allow_storage_mutations:
            warnings.append("ZFS creation is preview-only until enabled on appliance with sufficient RAM")
        commands.append(f"zpool create {name} {' '.join(devices)}")

    payload = {
        "name": name,
        "backend": backend,
        "devices": devices,
        "raid_level": raid_level,
    }
    token = secrets.token_urlsafe(24)
    db.add(
        ConfirmToken(
            token=token,
            operation="storage.pool.create",
            payload_hash=_payload_hash(payload),
            expires_at=_confirm_expiry(),
        )
    )
    db.commit()
    return {
        "warnings": warnings,
        "commands_preview": commands,
        "confirm_token": token,
        "plan": payload,
    }


def execute_pool_create(
    db: Session,
    *,
    name: str,
    backend: str,
    devices: list[str],
    raid_level: str | None,
    confirm_token: str,
) -> Job:
    payload = {
        "name": name,
        "backend": backend,
        "devices": devices,
        "raid_level": raid_level,
    }
    row = db.get(ConfirmToken, confirm_token)
    if row is None or row.operation != "storage.pool.create":
        raise Problem(400, "Invalid token", "confirm_token invalid", "CONFIRMATION_REQUIRED")
    from nasd.security import is_expired

    if is_expired(row.expires_at):
        db.delete(row)
        db.commit()
        raise Problem(400, "Token expired", "confirm_token expired", "CONFIRMATION_REQUIRED")
    if row.payload_hash != _payload_hash(payload):
        raise Problem(400, "Token mismatch", "request does not match confirmed plan", "CONFIRMATION_REQUIRED")

    running = (
        db.query(Job)
        .filter(Job.state.in_(("pending", "running")), Job.type == "pool.create")
        .first()
    )
    if running:
        raise Problem(409, "Pool busy", "another pool job is running", "POOL_BUSY")

    job = Job(
        id=str(uuid.uuid4()),
        type="pool.create",
        state="pending",
        progress=0,
        payload_json=json.dumps(payload),
    )
    db.add(job)
    db.delete(row)
    db.commit()
    db.refresh(job)
    return job


def list_pools(db: Session) -> list[Pool]:
    return db.query(Pool).order_by(Pool.name).all()
