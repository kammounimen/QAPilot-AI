import pytest
import requests


@pytest.mark.tc("TC-002-01")
def test_get_room_list_with_valid_token(base_url, admin_token):
    # GET /api/room avec token en cookie
    r = requests.get(
        f"{base_url}/api/room",
        cookies={"token": admin_token},
        timeout=10,
    )
    assert r.status_code == 200
    data = r.json()
    assert "rooms" in data
    rooms = data["rooms"]
    assert len(rooms) >= 1
    for room in rooms:
        # champs obligatoires
        assert {"roomid", "roomName", "type", "roomPrice"} <= room.keys()
        # types et contraintes de base
        assert isinstance(room["roomid"], int)
        assert isinstance(room["roomName"], str)
        assert room["type"] in ("Single", "Double", "Suite")
        assert isinstance(room["roomPrice"], int) and room["roomPrice"] > 0
