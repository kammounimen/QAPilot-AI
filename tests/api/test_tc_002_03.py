import pytest
import requests


@pytest.mark.tc("TC-002-03")
def test_room_list_without_auth(base_url):
    r = requests.get(f"{base_url}/api/room", timeout=10)
    assert r.status_code == 401
    assert r.json().get("error") == "Invalid credentials"
