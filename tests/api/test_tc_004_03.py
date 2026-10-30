import pytest
import requests


@pytest.mark.tc("TC-004-03")
def test_admin_login_invalid_credentials(base_url):
    r = requests.post(
        f"{base_url}/api/auth/login",
        json={"username": "admin", "password": "wrong"},
        timeout=10,
    )
    assert r.status_code == 401
    assert r.json().get("error") == "Invalid credentials"
