from typing import Any

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class UserPublic(BaseModel):
    id: str
    username: str
    role: str
    display_name: str = ""


class SystemStatus(BaseModel):
    version: str
    codename: str
    setup_complete: bool
    uptime_seconds: int


class Capabilities(BaseModel):
    profile: str
    ram_mb: int
    docker: bool
    zfs: bool
    virtualization: bool
    ai_photos: bool


class Disk(BaseModel):
    path: str
    size_bytes: int
    model: str | None = None
    serial: str | None = None
    smart_status: str | None = None


class PoolCreateRequest(BaseModel):
    name: str
    backend: str = "btrfs"
    devices: list[str]
    raid_level: str | None = None
    dry_run: bool = False
    confirm_token: str | None = None


class PoolPublic(BaseModel):
    id: str
    name: str
    backend: str
    raid_level: str | None
    state: str

    class Config:
        from_attributes = True


class ShareCreate(BaseModel):
    volume_id: str
    name: str
    protocols: list[str] = Field(default_factory=lambda: ["smb"])
    smb_options: dict[str, Any] = Field(default_factory=dict)


class SharePublic(BaseModel):
    id: str
    volume_id: str
    name: str
    protocols: list[str]

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "operator"
    display_name: str = ""


class UserUpdate(BaseModel):
    role: str | None = None
    display_name: str | None = None
    password: str | None = None


class SetupRequest(BaseModel):
    hostname: str
    admin_username: str
    admin_password: str
    timezone: str = "UTC"


class JobPublic(BaseModel):
    id: str
    type: str
    state: str
    progress: int
    message: str | None = None

    class Config:
        from_attributes = True


class FirewallConfig(BaseModel):
    ruleset: str | None = None
    dry_run: bool = False
