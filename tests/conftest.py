import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def nasd_env(tmp_path, monkeypatch) -> Path:
    root = tmp_path / "nasd"
    lib = root / "lib"
    lib.mkdir(parents=True)
    (root / "run").mkdir()
    monkeypatch.setenv("NASD_DATA_DIR", str(lib))
    monkeypatch.setenv("NASD_RUN_DIR", str(root / "run"))
    monkeypatch.setenv("NASD_COOKIE_SECURE", "false")
    monkeypatch.setenv("NASD_ALLOW_STORAGE_MUTATIONS", "false")
    monkeypatch.setenv("NASD_SAMBA_CONFIG_PATH", str(root / "samba.conf"))
    monkeypatch.setenv("NASD_NFTABLES_CONFIG_PATH", str(root / "nftables.conf"))
    monkeypatch.setenv("NASD_SEED_FILE", str(root / "missing-seed.json"))
    monkeypatch.setenv("NASD_INSTALL_PROFILE_FILE", str(root / "missing-profile.json"))

    from nasd.settings import settings

    monkeypatch.setattr(settings, "data_dir", lib)
    monkeypatch.setattr(settings, "run_dir", root / "run")
    monkeypatch.setattr(settings, "cookie_secure", False)
    monkeypatch.setattr(settings, "allow_storage_mutations", False)
    monkeypatch.setattr(settings, "samba_config_path", root / "samba.conf")
    monkeypatch.setattr(settings, "nftables_config_path", root / "nftables.conf")
    monkeypatch.setattr(settings, "seed_file", root / "missing-seed.json")
    monkeypatch.setattr(settings, "install_profile_file", root / "missing-profile.json")
    repo_apps = Path(__file__).resolve().parents[1] / "apps"
    monkeypatch.setattr(settings, "apps_dir", repo_apps)
    monkeypatch.setattr(settings, "compose_projects_dir", lib / "compose")

    from nasd.database import configure_engine, init_db

    configure_engine()
    db_file = lib / "config.db"
    for suffix in ("", "-wal", "-shm"):
        p = Path(str(db_file) + suffix)
        if p.exists():
            p.unlink()
    init_db()
    return root


@pytest.fixture
def client(nasd_env: Path, monkeypatch) -> TestClient:
    monkeypatch.setattr("nasd.core.storage.device_exists", lambda _p: True)
    monkeypatch.setattr("nasd.seed.load_seed_from_files", lambda _db: None)

    from nasd.app import create_app

    app = create_app()
    with TestClient(app) as c:
        yield c


@pytest.fixture
def admin_client(client: TestClient) -> TestClient:
    r = client.post(
        "/api/v1/system/setup",
        json={
            "hostname": "testnas",
            "admin_username": "admin",
            "admin_password": "correct-horse-battery-staple",
            "timezone": "UTC",
        },
    )
    assert r.status_code == 200, r.text
    r = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "correct-horse-battery-staple"},
    )
    assert r.status_code == 200, r.text
    return client
