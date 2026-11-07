import argparse
import json
from pathlib import Path

from pipeline.export import get_backend
from pipeline.junit_utils import load_all

MAPPING = Path("mapping.json")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="file")
    args = ap.parse_args()

    backend = get_backend(args.backend)
    mapping = (
        json.loads(MAPPING.read_text(encoding="utf-8")) if MAPPING.exists() else {}
    )
    blocking, defects = load_all()

    results = []
    for t in blocking + defects:
        results.append(
            {
                "tc_id": t["tc"],
                "key": mapping.get(t["tc"]),
                "test": t["test"],
                "status": t["status"],
                "duration": t["duration"],
                "message": t["message"],
                "source": t["source"],
            }
        )
    execution_id = backend.import_results(results)
    print(f"Résultats importés ({args.backend}) : {len(results)} tests -> {execution_id}")


if __name__ == "__main__":
    main()
