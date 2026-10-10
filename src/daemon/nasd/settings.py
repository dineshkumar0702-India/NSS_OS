from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="NASD_", env_file=".env", extra="ignore")

    data_dir: Path = Path("/var/lib/nasd")
    run_dir: Path = Path("/run/nasd")
    codename: str = "OpenNAS-Lite"
    version: str = "0.1.0"
    host: str = "127.0.0.1"
    port: int = 8741
    unix_socket: Path | None = None
    bind_tcp: bool = True
    session_ttl_hours: int = 24
    cookie_name: str = "nas_session"
    cookie_secure: bool = True
    allow_storage_mutations: bool = False
    allow_docker_ops: bool = False
    allow_system_upgrade: bool = False
    apps_dir: Path = Path("/usr/share/opennas/apps")
    compose_projects_dir: Path = Path("/var/lib/nasd/compose")
    seed_file: Path = Path("/usr/share/opennas/nasd/config.seed.json")
    install_profile_file: Path = Path("/var/lib/nasd/install-profile.json")
    samba_config_path: Path = Path("/etc/samba/smb.conf")
    nftables_config_path: Path = Path("/etc/nftables.conf")
    caddy_config_path: Path = Path("/etc/caddy/Caddyfile")

    @property
    def db_path(self) -> Path:
        return self.data_dir / "config.db"

    @property
    def master_key_path(self) -> Path:
        return self.data_dir / "master.key"


settings = Settings()
