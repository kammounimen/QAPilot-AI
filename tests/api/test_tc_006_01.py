import pytest
import requests


@pytest.mark.tc("TC-006-01")
def test_valid_login_and_get_rooms(base_url):
    # Étape 1 : login valide
    r_login = requests.post(
        f"{base_url}/api/auth/login",
        json={"username": "admin", "password": "password"},
        timeout=10,
    )
    assert r_login.status_code == 200
    token = r_login.json().get("token")
    assert token

    # Étape 2 : récupération des chambres avec le token en cookie
    r_rooms = requests.get(
        f"{base_url}/api/room",
        cookies={"token": token},
        timeout=10,
    )
    assert r_rooms.status_code == 200
    rooms = r_rooms.json().get("rooms")
    assert isinstance(rooms, list)
    assert len(rooms) >= 3

    # Vérification de la présence des champs attendus
    for room in rooms:
        assert {"roomid", "roomName", "type", "roomPrice"} <= room.keys()

    # Vérification que les trois chambres initiales sont présentes
    expected = {(1, "101"), (2, "102"), (3, "103")}
    actual = {(room["roomid"], room["roomName"]) for room in rooms}
    assert expected <= actual
