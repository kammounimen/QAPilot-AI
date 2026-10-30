import pytest
import requests


@pytest.mark.tc("TC-010-01")
def test_admin_login_success(base_url):
    r = requests.post(
        f"{base_url}/api/auth/login",
        json={"username": "admin", "password": "password"},
        timeout=10,
    )
    assert r.status_code == 200
    json_body = r.json()
    assert "token" in json_body
    assert isinstance(json_body["token"], str) and json_body["token"]
