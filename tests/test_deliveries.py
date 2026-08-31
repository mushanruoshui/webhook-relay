from fastapi.testclient import TestClient
from tests.test_events import _create_event_payload
from tests.test_subscriptions import _create_sub_payload

def test_all_deliveries(client: TestClient,auth_headers):
    client.post("/api/subscriptions", json=_create_sub_payload(), headers=auth_headers)
    client.post("/api/events", json=_create_event_payload(), headers=auth_headers)
    resp = client.get("/api/deliveries", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["total"] == 1
    assert resp.json()["items"][0]["status"] in ["delivered","retrying"]

def test_failed_deliveries(client: TestClient,auth_headers):
    client.post("/api/subscriptions", json=_create_sub_payload(), headers=auth_headers)
    client.post("/api/events", json=_create_event_payload(), headers=auth_headers)
    resp = client.get("/api/deliveries?status=failed", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["total"] == 0
    assert resp.json()["items"] == []

def test_limit_deliveries(client: TestClient,auth_headers):
    client.post("/api/subscriptions", json=_create_sub_payload(), headers=auth_headers)
    client.post("/api/events", json=_create_event_payload(), headers=auth_headers)
    resp = client.get("/api/deliveries?limit=1", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["total"] == 1

def test_trigger_retry(client, auth_headers):
    from app.database import factory
    from app.models import Delivery
    from datetime import datetime, timezone
    client.post("/api/subscriptions", json=_create_sub_payload(), headers=auth_headers)
    client.post("/api/events", json=_create_event_payload(), headers=auth_headers)
    db = factory()
    delivery = db.query(Delivery).first()
    delivery.next_attempt_at = datetime(2020, 1, 1, tzinfo=timezone.utc)
    db.commit()
    db.close()
    resp = client.post("/api/deliveries/retry", headers=auth_headers)
    assert resp.json()["retried"] > 0
    resp2 = client.get("/api/deliveries", headers=auth_headers)
    assert resp2.json()["items"][0]["attempt_count"] >= 2


