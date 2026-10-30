import os

import pytest
import requests
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture(scope="session")
def base_url():
    return os.getenv("BASE_URL", "http://localhost:8080")


@pytest.fixture(scope="session")
def admin_token(base_url):
    r = requests.post(
        f"{base_url}/api/auth/login",
        json={"username": "admin", "password": "password"},
        timeout=10,
    )
    assert r.status_code == 200
    return r.json()["token"]
