import pytest
import requests


@pytest.mark.tc("TC-001-04")
def test_login_malformed_json_returns_400(base_url):
    # DEF-001 : observé 500, attendu 400
    r = requests.post(
        f"{base_url}/api/auth/login",
        data="{bad",
        headers={"Content-Type": "application/json"},
        timeout=10,
    )
    assert r.status_code == 400