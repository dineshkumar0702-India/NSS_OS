def test_apps_catalog(admin_client):
    from nasd.database import get_session_factory
    from nasd.models import FeatureFlag

    with get_session_factory()() as db:
        db.merge(FeatureFlag(name="docker", enabled=1, source="user"))
        db.commit()
    res = admin_client.get("/api/v1/apps/catalog")
    assert res.status_code == 200
    ids = {i["id"] for i in res.json()["items"]}
    assert "jellyfin" in ids
    assert "pihole" in ids


def test_backup_run_job(admin_client):
    res = admin_client.post(
        "/api/v1/backups/run",
        json={"source_path": "/data", "target_path": "/data/backups/repo"},
    )
    assert res.status_code == 200
    job_id = res.json()["job_id"]
    job = admin_client.get(f"/api/v1/jobs/{job_id}").json()["job"]
    assert job["state"] == "success"
