from fastapi import APIRouter, Depends

from nasd.api import (
    apps,
    auth,
    backups,
    files,
    jobs,
    network,
    notifications,
    security,
    services,
    shares,
    snapshots,
    storage,
    system,
    users,
    updates,
    vms,
    vpn,
)
from nasd.deps import require_setup_complete

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(system.router)
api_router.include_router(auth.login_router)

protected = APIRouter(dependencies=[Depends(require_setup_complete)])
protected.include_router(auth.session_router)
protected.include_router(system.capabilities_router)
protected.include_router(storage.router)
protected.include_router(snapshots.router)
protected.include_router(backups.router)
protected.include_router(apps.router)
protected.include_router(vms.router)
protected.include_router(vpn.router)
protected.include_router(notifications.router)
protected.include_router(updates.router)
protected.include_router(users.router)
protected.include_router(shares.router)
protected.include_router(files.router)
protected.include_router(network.router)
protected.include_router(security.router)
protected.include_router(services.router)
protected.include_router(jobs.router)
api_router.include_router(protected)
