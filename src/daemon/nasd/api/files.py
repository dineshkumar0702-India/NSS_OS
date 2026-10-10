from pathlib import Path

from fastapi import APIRouter, Depends, Query

from nasd.deps import require_role
from nasd.errors import Problem
from nasd.models import User

router = APIRouter(prefix="/files", tags=["files"])

ALLOWED_ROOTS = (
    Path("/data"),
    Path("/mnt"),
    Path("/var/lib/nasd/files"),
)


def _resolve_path(raw: str) -> Path:
    candidate = Path(raw).expanduser()
    if not candidate.is_absolute():
        candidate = Path("/data") / candidate
    resolved = candidate.resolve()
    for root in ALLOWED_ROOTS:
        try:
            root_resolved = root.resolve()
        except OSError:
            continue
        if resolved == root_resolved or root_resolved in resolved.parents:
            return resolved
    raise Problem(403, "Path denied", "path outside allowed roots", "AUTH_FAILED")


@router.get("")
def list_files(
    path: str = Query("/data", description="Directory path"),
    _user: User = Depends(require_role("viewer")),
) -> dict:
    target = _resolve_path(path)
    if not target.exists():
        raise Problem(404, "Not found", "path does not exist", "NOT_FOUND")
    if not target.is_dir():
        raise Problem(400, "Not a directory", "path is not a directory", "VALIDATION_ERROR")
    items = []
    try:
        for entry in sorted(target.iterdir(), key=lambda p: p.name.lower()):
            try:
                stat = entry.stat()
                items.append(
                    {
                        "name": entry.name,
                        "path": str(entry),
                        "is_dir": entry.is_dir(),
                        "size_bytes": stat.st_size if entry.is_file() else None,
                    }
                )
            except OSError:
                continue
    except PermissionError:
        raise Problem(403, "Permission denied", "cannot read directory", "AUTH_FAILED")
    return {"path": str(target), "items": items}
