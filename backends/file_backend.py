import json
from datetime import UTC, datetime
from pathlib import Path

from backends.base import TestManagementBackend

ROOT = Path("reports/xray_mock")


class FileBackend(TestManagementBackend):
    def __init__(self, root: Path = ROOT):
        self.root = root
        self.tests_dir = root / "tests"
        self.tests_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        return self.tests_dir / f"{key}.json"

    def find_by_external_id(self, external_id: str) -> str | None:
        for f in self.tests_dir.glob("*.json"):
            data = json.loads(f.read_text(encoding="utf-8"))
            if data.get("external_id") == external_id:
                return data["key"]
        return None

    def create_test(self, case: dict) -> str:
        n = len(list(self.tests_dir.glob("*.json"))) + 1
        key = f"MOCK-{n}"
        self._write(key, case)
        return key

    def update_test(self, key: str, case: dict) -> None:
        self._write(key, case)

    def _write(self, key: str, case: dict) -> None:
        payload = {"key": key, "external_id": case["id"], **case}
        self._path(key).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def import_results(self, results: list[dict]) -> str:
        execution_id = "EXEC-" + datetime.now(UTC).strftime("%Y%m%d%H%M%S")
        out = self.root / f"{execution_id}.json"
        out.write_text(
            json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return execution_id
