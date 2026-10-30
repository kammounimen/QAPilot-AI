import pytest
import requests


@pytest.mark.tc("TC-001-01")
def test_login_valid_returns_token(base_url):
    # Envoi de la requête de connexion avec les identifiants admin valides
    r = requests.post(
        f"{base_url}/api/auth/login",
        json={"username": "admin", "password": "password"},
        timeout=10,
    )
    assert r.status_code == 200
    # Le corps doit contenir un champ token non vide
    json_body = r.json()
    assert "token" in json_body
    assert isinstance(json_body["token"], str) and json_body["token"]
