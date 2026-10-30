import pytest
import requests


@pytest.mark.tc("TC-012-04b")
def test_create_room_without_token_rejected(base_url):
    # REQ-012 critère 1 : création de chambre sans jeton refusée
    r = requests.post(
        f"{base_url}/api/room",
        json={
            "roomName": "999",
            "type": "Single",
            "accessible": True,
            "description": "test",
            "image": "x.jpg",
            "roomPrice": 100,
            "features": [],
        },
        timeout=10,
    )
    assert r.status_code in (401, 403)