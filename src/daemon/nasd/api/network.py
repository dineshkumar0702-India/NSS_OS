from fastapi import APIRouter, Depends

from nasd.core.network import list_interfaces
from nasd.deps import require_role
from nasd.models import User

router = APIRouter(prefix="/network", tags=["network"])


@router.get("/interfaces")
def network_interfaces(_user: User = Depends(require_role("viewer"))) -> dict:
    return {"items": list_interfaces()}
