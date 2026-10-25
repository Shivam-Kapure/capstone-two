import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"
    assert r.json()["version"]


def test_list_payments():
    r = client.get("/api/payments")
    assert r.status_code == 200
    statuses = {p["status"] for p in r.json()}
    assert {"COMPLETED", "PENDING", "FAILED"} <= statuses


def test_get_payment_and_missing():
    r = client.get("/api/payments/1")
    assert r.status_code == 200
    assert r.json()["id"] == 1

    r = client.get("/api/payments/99999")
    assert r.status_code == 404
    assert "not found" in r.json()["detail"]


def test_create_payment_adds_notification():
    before = len(client.get("/api/notifications").json())
    r = client.post(
        "/api/payments",
        json={"payer": "Test Payer", "payee": "Test Payee", "amount": 10.5, "currency": "USD"},
    )
    assert r.status_code == 201
    created = r.json()
    assert created["amount"] == 10.5
    assert client.get(f"/api/payments/{created['id']}").status_code == 200

    notes = client.get("/api/notifications").json()
    assert len(notes) == before + 1
    assert notes[0]["payment_id"] == created["id"]


@pytest.mark.parametrize(
    "payload",
    [
        {"payer": "", "payee": "Shop", "amount": 5, "currency": "INR"},
        {"payer": "A", "payee": "Shop", "amount": 0, "currency": "INR"},
        {"payer": "A", "payee": "Shop", "amount": 1.234, "currency": "INR"},
        {"payer": "A", "payee": "Shop", "amount": 5, "currency": "GBP"},
    ],
)
def test_create_payment_invalid(payload):
    r = client.post("/api/payments", json=payload)
    assert r.status_code == 422


def test_notifications_newest_first():
    r = client.get("/api/notifications")
    assert r.status_code == 200
    ids = [n["id"] for n in r.json()]
    assert ids and ids == sorted(ids, reverse=True)
