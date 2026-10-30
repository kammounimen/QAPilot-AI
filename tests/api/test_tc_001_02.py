import pytest
import requests


@pytest.mark.tc("TC-001-02")
def test_login_wrong_password_rejected(base_url):
    r = requests.post(
        f"{base_url}/api/auth/login",
        json={"username": "admin", "password": "wrong"},
        timeout=10,
    )
    assert r.status_code == 401
    assert r.json().get("error") == "Invalid credentials"
