import json
import os
from collections import defaultdict
from pathlib import Path

from pipeline.export import load_cases
from pipeline.junit_utils import load_all
from pipeline.validation_log import summary_table

LOG = Path("reports/llm_log.jsonl")
OUT = Path("reports/metrics.md")
# Prix en USD par million de tokens : à renseigner d'après la page tarifs Groq
PRICE_IN = float(os.getenv("PRICE_IN_PER_M", "0"))
PRICE_OUT = float(os.getenv("PRICE_OUT_PER_M", "0"))


def read_log() -> list[dict]:
    if not LOG.exists():
        return []
    rows = []
    for line in LOG.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def table(headers: list[str], rows: list[list]) -> str:
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def llm_section(rows: list[dict]) -> str:
    by_version: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_version[r.get("prompt_version", "?")].append(r)
    data = []
    for version, items in sorted(by_version.items()):
        tin = sum(r["input_tokens"] for r in items)
        tout = sum(r["output_tokens"] for r in items)
        dur = sum(r["duration_s"] for r in items)
        cost = (tin * PRICE_IN + tout * PRICE_OUT) / 1_000_000
        cost_txt = f"{cost:.4f} USD" if PRICE_IN or PRICE_OUT else "n/a (prix non renseignes)"
        data.append(
            [version, len(items), tin, tout, f"{dur:.1f}", f"{dur / len(items):.2f}", cost_txt]
        )
    total = [
        "TOTAL",
        len(rows),
        sum(r["input_tokens"] for r in rows),
        sum(r["output_tokens"] for r in rows),
        f"{sum(r['duration_s'] for r in rows):.1f}",
        "",
        "",
    ]
    headers = ["Prompt", "Appels", "Tokens in", "Tokens out", "Duree (s)", "Moy. (s)", "Cout"]
    return table(headers, [*data, total])


def coverage_section() -> str:
    cases = load_cases()
    req_files = {f.stem for f in Path("requirements").glob("REQ-*.md")}
    types: dict[str, set[str]] = defaultdict(set)
    for c in cases:
        types[c.get("requirement_id", "?")].add(c.get("type", "?"))
    covered = [r for r in req_files if types.get(r)]
    both = [r for r in req_files if {"nominal", "negative"} <= types.get(r, set())]
    blocking, defects = load_all()
    automated_ids = {t["tc"] for t in blocking + defects if t["tc"]}
    automated = [c for c in cases if c["id"] in automated_ids]
    api = [c for c in cases if c.get("layer") == "API"]
    api_auto = [c for c in api if c["id"] in automated_ids]
    n = len(req_files) or 1
    pct = f"{100 * len(covered) / n:.0f} %"
    rows = [
        ["Exigences avec au moins un cas", f"{len(covered)} / {len(req_files)} ({pct})"],
        ["Exigences avec cas nominal ET negatif", f"{len(both)} / {len(req_files)}"],
        ["Cas automatises (toutes couches)", f"{len(automated)} / {len(cases)}"],
        ["Cas API automatises", f"{len(api_auto)} / {len(api)}"],
    ]
    return table(["Indicateur", "Valeur"], rows)


def main() -> None:
    rows = read_log()
    parts = [
        "# Metriques QAPilot-AI",
        "",
        "## Appels LLM (reports/llm_log.jsonl)",
        "",
        llm_section(rows) if rows else "_Aucun log._",
        "",
        "## Validation JSON (reports/validation_log.jsonl)",
        "",
        summary_table(),
        "",
        "## Couverture et automatisation",
        "",
        coverage_section(),
        "",
    ]
    OUT.write_text("\n".join(parts), encoding="utf-8")
    print("\n".join(parts))
    print(f"Ecrit : {OUT}")


if __name__ == "__main__":
    main()
