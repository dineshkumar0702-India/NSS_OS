import json
import time

from nasd.models import Pool, Volume


def test_status_before_setup(client):
    r = client.get("/api/v1/system/status")
    assert r.status_code == 200
    assert r.json()["setup_complete"] is False


def test_setup_and_login(admin_client):
    r = admin_client.get("/api/v1/system/status")
    assert r.status_code == 200
    assert r.json()["setup_complete"] is True
    r = admin_client.get("/api/v1/auth/me")
    assert r.status_code == 200
    assert r.json()["username"] == "admin"
    assert r.json()["role"] == "owner"


def test_capabilities(admin_client):
    r = admin_client.get("/api/v1/system/capabilities")
    assert r.status_code == 200
    body = r.json()
    assert "profile" in body
    assert "ram_mb" in body


def test_pool_dry_run(admin_client):
    r = admin_client.post(
        "/api/v1/storage/pools",
        json={
            "name": "tank",
            "backend": "btrfs",
            "devices": ["/dev/sdb"],
            "dry_run": True,
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert "confirm_token" in data
    assert data["commands_preview"]


def test_share_requires_volume(admin_client):
    r = admin_client.post(
        "/api/v1/shares",
        json={"volume_id": "missing", "name": "media"},
    )
    assert r.status_code == 404


def test_share_create(admin_client):
    from nasd.database import get_session_factory

    with get_session_factory()() as db:
        pool = Pool(name="data-share-test", backend="btrfs", state="online", metadata_json="{}")
        db.add(pool)
        db.flush()
        vol = Volume(pool_id=pool.id, name="main", mount_path="/data/main")
        db.add(vol)
        db.commit()
        vol_id = vol.id

    r = admin_client.post(
        "/api/v1/shares",
        json={"volume_id": vol_id, "name": "media", "protocols": ["smb"]},
    )
    assert r.status_code == 200
    assert r.json()["name"] == "media"


def test_job_simulation(admin_client):
    plan = admin_client.post(
        "/api/v1/storage/pools",
        json={
            "name": "pool2",
            "backend": "btrfs",
            "devices": ["/dev/sdc"],
            "dry_run": True,
        },
    ).json()
    r = admin_client.post(
        "/api/v1/storage/pools",
        json={
            "name": "pool2",
            "backend": "btrfs",
            "devices": ["/dev/sdc"],
            "confirm_token": plan["confirm_token"],
        },
    )
    assert r.status_code == 200
    job_id = r.json()["job_id"]
    for _ in range(20):
        j = admin_client.get(f"/api/v1/jobs/{job_id}").json()
        if j["job"]["state"] in ("success", "failed"):
            break
        time.sleep(0.05)
    assert j["job"]["state"] == "success"
    assert j["result"]["status"] == "simulated"
