import argparse
import json
from pathlib import Path

from backends.base import TestManagementBackend
from backends.file_backend import FileBackend

MAPPING = Path("mapping.json")


def get_backend(name: str) -> TestManagementBackend:
    if name == "file":
        return FileBackend()
    raise SystemExit(f"Backend inconnu : {name}")


def load_cases() -> list[dict]:
    cases = []
    for f in sorted(Path("cases").glob("REQ-*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        items = data if isinstance(data, list) else data.get("cases", [])
        for c in items:
            c.setdefault("requirement_id", f.stem)
            cases.append(c)
    return cases


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="file")
    args = ap.parse_args()

    backend = get_backend(args.backend)
    mapping = json.loads(MAPPING.read_text(encoding="utf-8")) if MAPPING.exists() else {}

    created = updated = 0
    for case in load_cases():
        tc_id = case["id"]
        key = mapping.get(tc_id) or backend.find_by_external_id(tc_id)
        if key:
            backend.update_test(key, case)
            updated += 1
        else:
            key = backend.create_test(case)
            created += 1
        mapping[tc_id] = key

    MAPPING.write_text(
        json.dumps(mapping, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(f"Export {args.backend} : {created} créés, {updated} mis à jour, {len(mapping)} au total")


if __name__ == "__main__":
    main()