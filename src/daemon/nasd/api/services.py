from fastapi import APIRouter, Depends

from nasd.core.services import list_services
from nasd.deps import require_role
from nasd.models import User

router = APIRouter(prefix="/services", tags=["services"])


@router.get("")
def services_status(_user: User = Depends(require_role("viewer"))) -> dict:
    return {"items": list_services()}
