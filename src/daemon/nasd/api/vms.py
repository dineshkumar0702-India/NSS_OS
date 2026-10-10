from fastapi import APIRouter, Depends

from nasd.core.capabilities import get_capabilities
from nasd.deps import DbDep, require_role
from nasd.errors import Problem
from nasd.models import User

router = APIRouter(prefix="/vms", tags=["vms"])


@router.get("")
def list_vms(db: DbDep, _user: User = Depends(require_role("viewer"))) -> dict:
    caps = get_capabilities(db)
    if not caps.get("virtualization"):
        return {"items": [], "available": False, "message": "KVM not available on this system"}
    return {"items": [], "available": True, "message": "VM listing via libvirt planned; use Phase 5+ virt-install integration"}


@router.post("")
def create_vm(
    body: dict,
    db: DbDep,
    _user: User = Depends(require_role("admin")),
) -> dict:
    caps = get_capabilities(db)
    if not caps.get("virtualization"):
        raise Problem(403, "Unavailable", "virtualization not available", "CAPABILITY_DENIED")
    raise Problem(501, "Not implemented", "VM create API stub — libvirt integration next", "VALIDATION_ERROR")
