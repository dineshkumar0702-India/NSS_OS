import uuid
from datetime import datetime, timezone

from sqlalchemy import ForeignKey, Integer, LargeBinary, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from nasd.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class SystemConfig(Base):
    __tablename__ = "system_config"
    key: Mapped[str] = mapped_column(String, primary_key=True)
    value_json: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[str] = mapped_column(String, nullable=False, default=_utcnow)


class FeatureFlag(Base):
    __tablename__ = "feature_flags"
    name: Mapped[str] = mapped_column(String, primary_key=True)
    enabled: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    source: Mapped[str] = mapped_column(String, nullable=False, default="profile")


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String, nullable=False, default="")
    role: Mapped[str] = mapped_column(String, nullable=False, default="viewer")
    password_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    totp_secret_enc: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    webauthn_credentials_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(String, nullable=False, default=_utcnow)


class AuthSession(Base):
    __tablename__ = "sessions"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    expires_at: Mapped[str] = mapped_column(String, nullable=False)
    ip: Mapped[str | None] = mapped_column(String, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String, nullable=True)
    user: Mapped["User"] = relationship("User")


class ApiToken(Base):
    __tablename__ = "api_tokens"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    token_hash: Mapped[str] = mapped_column(String, nullable=False)
    scope: Mapped[str] = mapped_column(String, nullable=False, default="read-only")
    last_used_at: Mapped[str | None] = mapped_column(String, nullable=True)


class BlockDevice(Base):
    __tablename__ = "block_devices"
    path: Mapped[str] = mapped_column(String, primary_key=True)
    serial: Mapped[str | None] = mapped_column(String, nullable=True)
    model: Mapped[str | None] = mapped_column(String, nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    smart_status: Mapped[str | None] = mapped_column(String, nullable=True)
    pool_id: Mapped[str | None] = mapped_column(String, ForeignKey("pools.id"), nullable=True)


class Pool(Base):
    __tablename__ = "pools"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    backend: Mapped[str] = mapped_column(String, nullable=False)
    raid_level: Mapped[str | None] = mapped_column(String, nullable=True)
    state: Mapped[str] = mapped_column(String, nullable=False, default="online")
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class Volume(Base):
    __tablename__ = "volumes"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    pool_id: Mapped[str] = mapped_column(String, ForeignKey("pools.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    mount_path: Mapped[str] = mapped_column(String, nullable=False)
    quota_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    compression: Mapped[str | None] = mapped_column(String, nullable=True)
    __table_args__ = (UniqueConstraint("pool_id", "name", name="uq_volume_pool_name"),)


class Share(Base):
    __tablename__ = "shares"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    volume_id: Mapped[str] = mapped_column(String, ForeignKey("volumes.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    protocols: Mapped[str] = mapped_column(Text, nullable=False, default='["smb"]')
    smb_options_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    nfs_export_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class AclEntry(Base):
    __tablename__ = "acl_entries"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    share_id: Mapped[str] = mapped_column(String, ForeignKey("shares.id"), nullable=False)
    principal: Mapped[str] = mapped_column(String, nullable=False)
    permission: Mapped[str] = mapped_column(String, nullable=False)


class Snapshot(Base):
    __tablename__ = "snapshots"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    volume_id: Mapped[str] = mapped_column(String, ForeignKey("volumes.id"), nullable=False)
    backend_id: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[str] = mapped_column(String, nullable=False, default=_utcnow)
    retention_policy_id: Mapped[str | None] = mapped_column(String, nullable=True)


class BackupPolicy(Base):
    __tablename__ = "backup_policies"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    source_path: Mapped[str] = mapped_column(String, nullable=False)
    target_path: Mapped[str] = mapped_column(String, nullable=False)
    schedule_cron: Mapped[str | None] = mapped_column(String, nullable=True)
    enabled: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    config_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class AppInstance(Base):
    __tablename__ = "app_instances"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    template_id: Mapped[str] = mapped_column(String, nullable=False)
    state: Mapped[str] = mapped_column(String, nullable=False, default="stopped")
    compose_project: Mapped[str] = mapped_column(String, nullable=False)
    resource_limits_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class NotificationChannel(Base):
    __tablename__ = "notification_channels"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    type: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    config_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    enabled: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    type: Mapped[str] = mapped_column(String, nullable=False)
    state: Mapped[str] = mapped_column(String, nullable=False, default="pending")
    progress: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    result_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[str] = mapped_column(String, nullable=False, default=_utcnow)
    finished_at: Mapped[str | None] = mapped_column(String, nullable=True)


class JobLogLine(Base):
    __tablename__ = "job_log_lines"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(String, ForeignKey("jobs.id"), nullable=False)
    ts: Mapped[str] = mapped_column(String, nullable=False, default=_utcnow)
    line: Mapped[str] = mapped_column(Text, nullable=False)


class ConfirmToken(Base):
    __tablename__ = "confirm_tokens"
    token: Mapped[str] = mapped_column(String, primary_key=True)
    operation: Mapped[str] = mapped_column(String, nullable=False)
    payload_hash: Mapped[str] = mapped_column(String, nullable=False)
    expires_at: Mapped[str] = mapped_column(String, nullable=False)


class AuditEvent(Base):
    __tablename__ = "audit_events"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    ts: Mapped[str] = mapped_column(String, nullable=False, default=_utcnow)
    actor_user_id: Mapped[str | None] = mapped_column(String, nullable=True)
    action: Mapped[str] = mapped_column(String, nullable=False)
    target_type: Mapped[str | None] = mapped_column(String, nullable=True)
    target_id: Mapped[str | None] = mapped_column(String, nullable=True)
    outcome: Mapped[str] = mapped_column(String, nullable=False)
    meta_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
