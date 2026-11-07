import hashlib
import json
import sys
from pathlib import Path

from pipeline.junit_utils import load_all

SNAP_DIR = Path("reports/repro")


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def normalized_report() -> str:
    """report.md sans les lignes qui varient d'un run à l'autre (durées)."""
    text = Path("reports/report.md").read_text(encoding="utf-8")
    lines = [ln for ln in text.splitlines() if "Durée" not in ln]
    return sha_bytes("\n".join(lines).encode("utf-8"))


def snapshot() -> dict:
    blocking, defects = load_all()
    results = sorted(
        [t["tc"] or "", t["test"], t["status"], t["source"]]
        for t in blocking + defects
    )
    return {
        "cases": {f.name: sha_file(f) for f in sorted(Path("cases").glob("REQ-*.json"))},
        "mapping": sha_file(Path("mapping.json")),
        "xray_mock": {
            f.name: sha_file(f)
            for f in sorted(Path("reports/xray_mock/tests").glob("*.json"))
        },
        "results": results,
        "report_md": normalized_report(),
    }


def compare(a: dict, b: dict) -> list[str]:
    return [key for key, value in a.items() if value != b.get(key)]


def main() -> None:
    if len(sys.argv) < 3:
        raise SystemExit("usage: repro snapshot <nom> | repro compare <a> <b>")
    SNAP_DIR.mkdir(parents=True, exist_ok=True)
    if sys.argv[1] == "snapshot":
        path = SNAP_DIR / f"{sys.argv[2]}.json"
        path.write_text(
            json.dumps(snapshot(), ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        print(f"Empreinte écrite : {path}")
    elif sys.argv[1] == "compare":
        a = json.loads((SNAP_DIR / f"{sys.argv[2]}.json").read_text(encoding="utf-8"))
        b = json.loads((SNAP_DIR / f"{sys.argv[3]}.json").read_text(encoding="utf-8"))
        diffs = compare(a, b)
        print(
            f"Comparé : {len(a['cases'])} fichiers de cas, "
            f"{len(a['xray_mock'])} tests exportés, {len(a['results'])} résultats"
        )
        if diffs:
            print("DIFFÉRENCES dans : " + ", ".join(diffs))
            raise SystemExit(1)
        print("IDENTIQUE : les deux exécutions sont reproductibles")
    else:
        raise SystemExit("commande inconnue")


if __name__ == "__main__":
    main()
