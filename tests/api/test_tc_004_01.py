import pytest
import requests


@pytest.mark.tc("TC-004-01")
def test_admin_login_success(base_url):
    r = requests.post(
        f"{base_url}/api/auth/login",
        json={"username": "admin", "password": "password"},
        timeout=10,
    )
    assert r.status_code == 200
    assert "token" in r.json()
    assert r.json()["token"]
