import os

import pytest
import requests
from dotenv import load_dotenv

from known_gaps import INCONSISTENT_CASES, REASON
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


def pytest_collection_modifyitems(config, items):
    for item in items:
        marker = item.get_closest_marker("tc")
        if marker and marker.args and marker.args[0] in INCONSISTENT_CASES:
            item.add_marker(pytest.mark.xfail(reason=REASON, strict=False))