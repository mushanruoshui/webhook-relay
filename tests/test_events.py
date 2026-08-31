from fastapi.testclient import TestClient

def _create_event_payload():
    return {
        "event_type" : "order.created",
        "payload" : {}
    }

# 无接口密匙
def test_no_api_create_events(client: TestClient):
    resp = client.post("/api/events", json=_create_event_payload())
    assert resp.status_code == 422

def test_create_events(client, auth_headers):
    resp = client.post("/api/events", json=_create_event_payload(), headers=auth_headers)
    assert resp.status_code == 202

def test_get_no_events(client, auth_headers):
    resp = client.get("/api/events", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []

def test_get_events(client, auth_headers):
    client.post("/api/events", json=_create_event_payload(), headers=auth_headers)
    resp = client.get("/api/events", headers=auth_headers)
    assert resp.status_code == 200

def test_get_event(client, auth_headers):
    client.post("/api/events", json=_create_event_payload(), headers=auth_headers)
    resp = client.get("/api/events/1", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == 1
    assert resp.json()["event_type"] == "order.created"

def test_get_no_event(client, auth_headers):
    resp = client.get("/api/events/1", headers=auth_headers)
    assert resp.status_code == 404

def test_deliver_event(client, auth_headers):
    payload = {
        "url": "http://127.0.0.1:9000/hook",
        "secret": "a-very-secret-key",
        "event_types": ["order.created"],
        "description": "测试订阅",
    }
    client.post("/api/subscriptions", json=payload, headers=auth_headers)
    client.post("/api/events", json=_create_event_payload(), headers=auth_headers)
    resp = client.get("/api/events/1", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()["deliveries"]) == 1



