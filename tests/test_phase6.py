def test_updates_dry_run(admin_client):
    r = admin_client.post("/api/v1/updates/apply", json={"dry_run": True})
    assert r.status_code == 200
    data = r.json()
    assert "confirm_token" in data
    assert "snapshot_label" in data


def test_updates_apply_simulated(admin_client):
    plan = admin_client.post("/api/v1/updates/apply", json={"dry_run": True}).json()
    r = admin_client.post(
        "/api/v1/updates/apply",
        json={
            "confirm_token": plan["confirm_token"],
            "snapshot_label": plan["snapshot_label"],
        },
    )
    assert r.status_code == 200
    job_id = r.json()["job_id"]
    job = admin_client.get(f"/api/v1/jobs/{job_id}").json()["job"]
    assert job["state"] == "success"


def test_security_advisor(admin_client):
    r = admin_client.get("/api/v1/security/advisor")
    assert r.status_code == 200
    body = r.json()
    assert "score" in body
    assert "findings" in body


def test_config_export(admin_client):
    r = admin_client.get("/api/v1/system/config/export")
    assert r.status_code == 200
    assert r.json()["schema_version"] == 1
    assert "signature" in r.json()
