import argparse
import json

from pipeline.export import get_backend, mapping_path
from pipeline.junit_utils import load_all


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="file")
    args = ap.parse_args()

    backend = get_backend(args.backend)
    path = mapping_path(args.backend)
    mapping = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    blocking, defects = load_all()

    results = [
        {
            "tc_id": t["tc"],
            "key": mapping.get(t["tc"]),
            "test": t["test"],
            "status": t["status"],
            "duration": t["duration"],
            "message": t["message"],
            "source": t["source"],
        }
        for t in blocking + defects
    ]
    execution_id = backend.import_results(results)
    print(f"Résultats importés ({args.backend}) : {len(results)} tests -> {execution_id}")


if __name__ == "__main__":
    main()