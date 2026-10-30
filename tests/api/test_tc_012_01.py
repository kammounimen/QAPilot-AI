import pytest
import requests


@pytest.mark.tc("TC-012-01")
def test_room_list_without_token_returns_unauthorized(base_url):
    # Send request without authentication cookie
    r = requests.get(f"{base_url}/api/room", timeout=10)
    # Expected unauthorized or forbidden according to the test case
    assert r.status_code in (401, 403)
    # The response should contain a JSON error indication
    json_body = r.json()
    assert isinstance(json_body, dict)
    assert any(key in json_body for key in ("error", "errors"))
