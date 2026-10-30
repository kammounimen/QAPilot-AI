import pytest
import requests


@pytest.mark.tc("TC-006-02")
def test_login_invalid_credentials_returns_401(base_url):
    r = requests.post(
        f"{base_url}/api/auth/login",
        json={"username": "admin", "password": "wrong"},
        timeout=10,
    )
    assert r.status_code == 401
    assert r.json().get("error") == "Invalid credentials"
