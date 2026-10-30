import pytest
import requests


@pytest.mark.tc("TC-002-01")
def test_room_list_returns_rooms(base_url):
    r = requests.get(f"{base_url}/api/room", timeout=10)
    assert r.status_code == 200
    rooms = r.json()["rooms"]
    assert len(rooms) >= 1
    for room in rooms:
        assert {"roomid", "roomName", "type", "roomPrice"} <= room.keys()
        assert room["roomPrice"] > 0
