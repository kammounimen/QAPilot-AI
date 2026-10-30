import pytest
import requests


@pytest.mark.tc("TC-012-02")
def test_room_list_invalid_token_returns_unauthorized(base_url):
    # Use an invalid token in the cookie as per test requirements
    r = requests.get(
        f"{base_url}/api/room",
        cookies={"token": "invalid_token"},
        timeout=10,
    )
    assert r.status_code in (401, 403)
