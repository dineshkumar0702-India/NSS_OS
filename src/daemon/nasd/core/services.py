import subprocess

DEFAULT_UNITS = [
    "avahi-daemon.service",
    "caddy.service",
    "nftables.service",
    "fail2ban.service",
    "smbd.service",
    "nfs-server.service",
    "docker.service",
]


def unit_status(name: str) -> dict:
    state = "unknown"
    active = "unknown"
    if _which("systemctl"):
        try:
            active = subprocess.check_output(
                ["systemctl", "is-active", name], text=True, stderr=subprocess.DEVNULL
            ).strip()
            state = subprocess.check_output(
                ["systemctl", "is-enabled", name], text=True, stderr=subprocess.DEVNULL
            ).strip()
        except subprocess.CalledProcessError as exc:
            active = exc.stdout.strip() if exc.stdout else "inactive"
    return {"unit": name, "active": active, "enabled": state}


def list_services(units: list[str] | None = None) -> list[dict]:
    names = units or DEFAULT_UNITS
    return [unit_status(u) for u in names]


def _which(cmd: str) -> bool:
    from shutil import which

    return which(cmd) is not None
