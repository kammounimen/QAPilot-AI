import json
import time
from collections import defaultdict
from pathlib import Path

LOG = Path("reports/validation_log.jsonl")


def log_validation(stage: str, item: str, attempt: int, valid: bool, error: str = "") -> None:
    LOG.parent.mkdir(exist_ok=True)
    row = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "stage": stage,
        "item": item,
        "attempt": attempt,
        "valid": valid,
        "error": error[:200],
    }
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def summary_table() -> str:
    if not LOG.exists():
        return "_Aucune validation journalisee._"
    rows = [json.loads(x) for x in LOG.read_text(encoding="utf-8").splitlines() if x.strip()]
    by_stage: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_stage[r["stage"]].append(r)
    lines = [
        "| Etape | Elements | Valide au 1er essai | Retries | Echec final |",
        "|---|---|---|---|---|",
    ]
    for stage, items in sorted(by_stage.items()):
        names = {r["item"] for r in items}
        first = [r for r in items if r["attempt"] == 1]
        first_ok = sum(1 for r in first if r["valid"])
        retries = sum(1 for r in items if r["attempt"] > 1)
        ok_items = {r["item"] for r in items if r["valid"]}
        pct = f"{100 * first_ok / len(first):.0f} %" if first else "n/a"
        lines.append(
            f"| {stage} | {len(names)} | {first_ok} / {len(first)} ({pct}) "
            f"| {retries} | {len(names - ok_items)} |"
        )
    return "\n".join(lines)
