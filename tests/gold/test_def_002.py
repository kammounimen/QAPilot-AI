import pytest
import requests


@pytest.mark.tc("TC-012-02b")
def test_messages_without_token_rejected(base_url):
    # DEF-002 : observé 200, attendu 401 ou 403
    r = requests.get(f"{base_url}/api/message", timeout=10)
    assert r.status_code in (401, 403)


@pytest.mark.tc("TC-012-03b")
def test_messages_invalid_token_rejected(base_url):
    # DEF-002 : observé 200, attendu 401 ou 403
    r = requests.get(
        f"{base_url}/api/message",
        cookies={"token": "invalid_token"},
        timeout=10,
    )
    assert r.status_code in (401, 403)