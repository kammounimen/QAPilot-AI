import pytest
import requests


@pytest.mark.tc("TC-001-01")
def test_login_valid_returns_token(base_url):
    r = requests.post(
        f"{base_url}/api/auth/login",
        json={"username": "admin", "password": "password"},
        timeout=10,
    )
    assert r.status_code == 200
    assert r.json()["token"]


@pytest.mark.tc("TC-001-02")
def test_login_wrong_password_rejected(base_url):
    r = requests.post(
        f"{base_url}/api/auth/login",
        json={"username": "admin", "password": "wrong"},
        timeout=10,
    )
    assert r.status_code == 401


@pytest.mark.tc("TC-010-01")
def test_messages_require_token_and_list(base_url, admin_token):
    r = requests.get(f"{base_url}/api/message", cookies={"token": admin_token}, timeout=10)
    assert r.status_code == 200
    assert "messages" in r.json()
