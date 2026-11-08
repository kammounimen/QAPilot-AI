import os
from datetime import UTC, datetime

import requests
from dotenv import load_dotenv

from backends.base import TestManagementBackend

load_dotenv(override=True)

XRAY_API = "https://xray.cloud.getxray.app/api/v2"
TIMEOUT = 30
RANK = {"FAILED": 2, "PASSED": 1, "TODO": 0}
STATUS = {"passed": "PASSED", "failed": "FAILED"}


def adf(lines: list[str]) -> dict:
    """Texte au format Atlassian Document Format (exigé par l'API Jira v3)."""
    content = [
        {"type": "paragraph", "content": [{"type": "text", "text": ln}]}
        for ln in lines
        if ln.strip()
    ]
    return {"type": "doc", "version": 1, "content": content}


def describe(case: dict) -> list[str]:
    lines = [
        f"Exigence : {case.get('requirement_id', '?')}",
        f"Couche : {case.get('layer', '?')} | Type : {case.get('type', '?')}",
        f"Priorité : {case.get('priority', '?')}",
        "Préconditions :",
    ]
    lines += [f"- {p}" for p in case.get("preconditions", [])]
    lines.append("Étapes :")
    for i, step in enumerate(case.get("steps", []), 1):
        lines.append(f"{i}. {step.get('action', '')}")
        lines.append(f"   Attendu : {step.get('expected', '')}")
    return lines


class XrayBackend(TestManagementBackend):
    def __init__(self) -> None:
        self.jira = os.environ["JIRA_URL"].rstrip("/")
        self.auth = (os.environ["JIRA_USER"], os.environ["JIRA_API_TOKEN"])
        self.project = os.environ["JIRA_PROJECT_KEY"]
        self.session = requests.Session()
        self._jwt: str | None = None

    def _call(self, method: str, url: str, **kwargs):
        r = self.session.request(method, url, timeout=TIMEOUT, **kwargs)
        if not r.ok:
            raise RuntimeError(f"{method} {url} -> {r.status_code} : {r.text[:300]}")
        return r

    def _token(self) -> str:
        if self._jwt is None:
            r = self._call(
                "POST",
                f"{XRAY_API}/authenticate",
                json={
                    "client_id": os.environ["XRAY_CLIENT_ID"],
                    "client_secret": os.environ["XRAY_CLIENT_SECRET"],
                },
            )
            self._jwt = r.json()
        return self._jwt

    @staticmethod
    def _fields(case: dict) -> dict:
        return {
            "summary": f"{case['id']} - {case['title']}"[:250],
            "description": adf(describe(case)),
            "labels": [case["id"], case.get("requirement_id", "REQ-UNKNOWN")],
        }

    def find_by_external_id(self, external_id: str) -> str | None:
        jql = (
            f'project = "{self.project}" AND issuetype = Test '
            f'AND labels = "{external_id}"'
        )
        r = self._call(
            "POST",
            f"{self.jira}/rest/api/3/search/jql",
            auth=self.auth,
            json={"jql": jql, "fields": ["summary"], "maxResults": 1},
        )
        issues = r.json().get("issues", [])
        return issues[0]["key"] if issues else None

    def create_test(self, case: dict) -> str:
        fields = self._fields(case)
        fields["project"] = {"key": self.project}
        fields["issuetype"] = {"name": "Test"}
        r = self._call(
            "POST",
            f"{self.jira}/rest/api/3/issue",
            auth=self.auth,
            json={"fields": fields},
        )
        return r.json()["key"]

    def update_test(self, key: str, case: dict) -> None:
        self._call(
            "PUT",
            f"{self.jira}/rest/api/3/issue/{key}",
            auth=self.auth,
            json={"fields": self._fields(case)},
        )

    def import_results(self, results: list[dict]) -> str:
        per_test: dict[str, str] = {}
        for r in results:
            key = r.get("key")
            if not key:
                continue  # test hors cas générés : pas de Test Jira correspondant
            status = STATUS.get(r["status"], "TODO")
            if RANK[status] >= RANK[per_test.get(key, "TODO")]:
                per_test[key] = status
        stamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M")
        payload = {
            "info": {
                "project": self.project,
                "summary": f"QAPilot-AI : exécution du {stamp} UTC",
            },
            "tests": [{"testKey": k, "status": s} for k, s in sorted(per_test.items())],
        }
        r = self._call(
            "POST",
            f"{XRAY_API}/import/execution",
            headers={"Authorization": f"Bearer {self._token()}"},
            json=payload,
        )
        return r.json().get("key", "?")