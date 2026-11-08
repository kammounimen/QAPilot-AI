import pytest

from backends.xray_backend import XrayBackend


class Resp:
    def __init__(self, data=None, status=200):
        self._data = data
        self.status_code = status
        self.ok = status < 400
        self.text = str(data)

    def json(self):
        return self._data


class FakeSession:
    def __init__(self, handler):
        self.handler = handler
        self.calls = []

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        return self.handler(method, url, kwargs)


@pytest.fixture
def backend(monkeypatch):
    monkeypatch.setenv("JIRA_URL", "https://example.atlassian.net")
    monkeypatch.setenv("JIRA_USER", "u@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "x")
    monkeypatch.setenv("JIRA_PROJECT_KEY", "QAP")
    monkeypatch.setenv("XRAY_CLIENT_ID", "id")
    monkeypatch.setenv("XRAY_CLIENT_SECRET", "secret")
    return XrayBackend()


CASE = {"id": "TC-001-01", "title": "Login", "requirement_id": "REQ-001", "steps": []}


def test_find_returns_existing_key(backend):
    backend.session = FakeSession(lambda *_: Resp({"issues": [{"key": "QAP-5"}]}))
    assert backend.find_by_external_id("TC-001-01") == "QAP-5"


def test_find_returns_none_when_absent(backend):
    backend.session = FakeSession(lambda *_: Resp({"issues": []}))
    assert backend.find_by_external_id("TC-001-01") is None


def test_create_sets_label_and_issue_type(backend):
    backend.session = FakeSession(lambda *_: Resp({"key": "QAP-9"}))
    assert backend.create_test(CASE) == "QAP-9"
    fields = backend.session.calls[0][2]["json"]["fields"]
    assert "TC-001-01" in fields["labels"]
    assert fields["issuetype"] == {"name": "Test"}


def test_import_aggregates_and_skips_unmapped(backend):
    def handler(method, url, kwargs):
        if url.endswith("/authenticate"):
            return Resp("jwt-value")
        return Resp({"key": "QAP-100"})

    backend.session = FakeSession(handler)
    results = [
        {"key": "QAP-1", "status": "passed"},
        {"key": "QAP-1", "status": "failed"},
        {"key": "QAP-2", "status": "xfail"},
        {"key": None, "status": "passed"},
    ]
    assert backend.import_results(results) == "QAP-100"
    sent = backend.session.calls[-1][2]["json"]["tests"]
    assert sent == [
        {"testKey": "QAP-1", "status": "FAILED"},
        {"testKey": "QAP-2", "status": "TODO"},
    ]


def test_http_error_raises(backend):
    backend.session = FakeSession(lambda *_: Resp("boom", status=401))
    with pytest.raises(RuntimeError):
        backend.find_by_external_id("TC-001-01")