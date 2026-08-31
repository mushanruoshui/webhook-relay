"""

运行：在项目根目录执行  pytest tests/ -v
"""
from fastapi.testclient import TestClient


def _create_sub_payload(url="http://127.0.0.1:9000/hook"):
    """构造一个合法的订阅创建请求体。"""
    return {
        "url": url,
        "secret": "a-very-secret-key",
        "event_types": ["order.created"],
        "description": "测试订阅",
    }


# ---------- 认证 ----------

def test_no_api_key_rejected(client: TestClient):
    """不带 API key 的请求必须被拒绝（认证生效）。"""
    resp = client.post("/api/subscriptions", json=_create_sub_payload())
    assert resp.status_code == 422  # Header(...) 必填缺失 → 422


def test_wrong_api_key_rejected(client: TestClient):
    """错误的 API key 必须被拒绝。"""
    resp = client.post(
        "/api/subscriptions",
        json=_create_sub_payload(),
        headers={"X-API-Key": "wrong-key"},
    )
    assert resp.status_code == 401


# ---------- 创建 ----------

def test_create_subscription(client: TestClient, auth_headers):
    """创建成功：201 + 返回体里有 id，且 is_active 默认 True。"""
    resp = client.post("/api/subscriptions", json=_create_sub_payload(), headers=auth_headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] > 0
    assert body["is_active"] is True
    assert body["event_types"] == ["order.created"]


def test_create_subscription_invalid_secret(client: TestClient, auth_headers):
    """secret 少于 8 位：Pydantic 校验拦截，返回 422。"""
    payload = _create_sub_payload()
    payload["secret"] = "short"  # min_length=8
    resp = client.post("/api/subscriptions", json=payload, headers=auth_headers)
    assert resp.status_code == 422


# ---------- 查询 ----------

def test_list_subscriptions(client: TestClient, auth_headers):
    """创建两条后，列表应该返回恰好这两条。"""
    client.post("/api/subscriptions", json=_create_sub_payload(), headers=auth_headers)
    client.post(
        "/api/subscriptions",
        json=_create_sub_payload(url="http://127.0.0.1:9001/hook"),
        headers=auth_headers,
    )
    resp = client.get("/api/subscriptions", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 2


# ---------- 删除 ----------

def test_delete_subscription(client: TestClient, auth_headers):
    """删除后再查列表应该为空。"""
    resp = client.post("/api/subscriptions", json=_create_sub_payload(), headers=auth_headers)
    sub_id = resp.json()["id"]

    resp = client.delete(f"/api/subscriptions/{sub_id}", headers=auth_headers)
    assert resp.status_code == 204

    resp = client.get("/api/subscriptions", headers=auth_headers)
    assert resp.json() == []
