import subprocess

from fastapi import APIRouter, Depends

from nasd.audit import audit_log
from nasd.core.render import write_nftables_config
from nasd.deps import DbDep, require_role
from nasd.schemas import FirewallConfig
from nasd.models import User

router = APIRouter(prefix="/security", tags=["security"])


@router.get("/firewall")
def get_firewall(db: DbDep, _user: User = Depends(require_role("admin"))) -> dict:
    from nasd.settings import settings

    if settings.nftables_config_path.is_file():
        return {"ruleset": settings.nftables_config_path.read_text(encoding="utf-8")}
    return {"ruleset": ""}


@router.put("/firewall")
def put_firewall(
    body: FirewallConfig,
    db: DbDep,
    user: User = Depends(require_role("admin")),
) -> dict:
    ruleset = body.ruleset
    if body.dry_run and ruleset:
        try:
            subprocess.run(
                ["nft", "-c", "-f", "-"],
                input=ruleset,
                text=True,
                check=True,
                capture_output=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            from nasd.errors import Problem

            raise Problem(400, "Invalid ruleset", str(exc), "VALIDATION_ERROR")
        return {"status": "valid"}
    write_nftables_config(db, ruleset)
    audit_log(db, actor_user_id=user.id, action="security.firewall.update", outcome="success")
    db.commit()
    return {"status": "applied"}
