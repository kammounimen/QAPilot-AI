import html
import re
from collections import Counter, defaultdict
from pathlib import Path

from pipeline.export import load_cases
from pipeline.junit_utils import load_all

OUT = Path("reports")


def requirement_info() -> dict[str, dict]:
    info = {}
    for f in sorted(Path("requirements").glob("REQ-*.md")):
        text = f.read_text(encoding="utf-8")
        title = text.splitlines()[0].lstrip("# ").strip()
        m = re.search(r"Priorité\*\*\s*:\s*(\S+)", text)
        info[f.stem] = {"title": title, "priority": m.group(1) if m else "?"}
    return info


def tc_status(tests: list[dict]) -> str:
    if not tests:
        return "non automatisé"
    states = {t["status"] for t in tests}
    if "failed" in states:
        failed = [t for t in tests if t["status"] == "failed"]
        if all(t["source"] == "defects" for t in failed):
            return "défaut connu"
        return "échec"
    if "passed" in states:
        return "réussi"
    if "xfail" in states:
        return "xfail (écart de génération)"
    return "ignoré"


def md_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = ["| " + " | ".join(headers) + " |"]
    lines.append("|" + "|".join("---" for _ in headers) + "|")
    for r in rows:
        lines.append("| " + " | ".join(str(c).replace("|", "/") for c in r) + " |")
    return "\n".join(lines)


def html_table(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f"<th>{html.escape(h)}</th>" for h in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{html.escape(str(c))}</td>" for c in r) + "</tr>"
        for r in rows
    )
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def main() -> None:
    blocking, defects = load_all()
    tests = blocking + defects
    cases = sorted(load_cases(), key=lambda c: c["id"])
    reqs = requirement_info()

    by_tc: dict[str, list[dict]] = defaultdict(list)
    for t in tests:
        by_tc[t["tc"] or "SANS-TC"].append(t)

    # --- Chiffres globaux (tous calculés ici, jamais par le LLM)
    counts = Counter(t["status"] for t in blocking)
    done = counts["passed"] + counts["failed"]
    rate = f"{100 * counts['passed'] / done:.1f} %" if done else "n/a"
    duration = sum(t["duration"] for t in tests)

    statuses = {c["id"]: tc_status(by_tc.get(c["id"], [])) for c in cases}
    automated = sum(1 for s in statuses.values() if s != "non automatisé")
    by_layer = Counter(c.get("layer", "?") for c in cases)
    auto_layer = Counter(
        c.get("layer", "?") for c in cases if statuses[c["id"]] != "non automatisé"
    )

    summary = [
        ["Tests exécutés (suite bloquante)", len(blocking)],
        ["Réussis", counts["passed"]],
        ["Échoués", counts["failed"]],
        ["xfail (écarts de génération)", counts["xfail"]],
        ["Taux de réussite (réussis / réussis+échoués)", rate],
        ["Défauts connus détectés (suite défauts)", sum(1 for t in defects if t["status"] == "failed")],
        ["Durée cumulée des tests (s)", f"{duration:.1f}"],
        ["Cas de test au total", len(cases)],
        ["Cas automatisés", f"{automated} / {len(cases)}"],
    ]
    for layer in sorted(by_layer):
        summary.append([f"Cas {layer} automatisés", f"{auto_layer[layer]} / {by_layer[layer]}"])

    # --- Matrice REQ -> TC -> test -> résultat
    matrix = []
    for c in cases:
        req = c.get("requirement_id", "?")
        prio = reqs.get(req, {}).get("priority", "?")
        names = ", ".join(t["test"] for t in by_tc.get(c["id"], [])) or "-"
        matrix.append([req, prio, c["id"], c.get("layer", "?"), c["title"], names, statuses[c["id"]]])

    case_ids = {c["id"] for c in cases}
    extra = [
        [tc, t["test"], t["status"], t["source"]]
        for tc, ts in sorted(by_tc.items())
        if tc not in case_ids
        for t in ts
    ]

    failures = [
        [t["tc"] or "-", t["test"], t["source"], t["message"]]
        for t in tests
        if t["status"] == "failed"
    ]

    # --- Couverture des exigences
    req_rows = []
    for req, info in reqs.items():
        req_cases = [c["id"] for c in cases if c.get("requirement_id") == req]
        ok = sum(1 for cid in req_cases if statuses[cid] == "réussi")
        req_rows.append([req, info["title"], info["priority"], len(req_cases), ok])

    sections = [
        ("Synthèse", ["Indicateur", "Valeur"], summary),
        ("Matrice de traçabilité REQ → TC → test → résultat",
         ["REQ", "Priorité", "TC", "Couche", "Titre", "Test(s)", "Résultat"], matrix),
        ("Couverture par exigence",
         ["REQ", "Titre", "Priorité", "Cas", "Cas réussis"], req_rows),
        ("Échecs et défauts connus", ["TC", "Test", "Suite", "Message"], failures),
        ("Tests gold hors cas générés", ["TC", "Test", "Statut", "Suite"], extra),
    ]

    md = ["# Rapport de synthèse QAPilot-AI", ""]
    page = ["<h1>Rapport de synthèse QAPilot-AI</h1>"]
    for title, headers, rows in sections:
        md += [f"## {title}", "", md_table(headers, rows) if rows else "_Aucun._", ""]
        page.append(f"<h2>{html.escape(title)}</h2>")
        page.append(html_table(headers, rows) if rows else "<p><em>Aucun.</em></p>")

    css = (
        "body{font-family:sans-serif;margin:2rem}"
        "table{border-collapse:collapse;margin-bottom:1.5rem}"
        "td,th{border:1px solid #bbb;padding:4px 8px;text-align:left}"
        "th{background:#eee}"
    )
    OUT.mkdir(exist_ok=True)
    (OUT / "report.md").write_text("\n".join(md), encoding="utf-8")
    (OUT / "report.html").write_text(
        f"<!doctype html><html><head><meta charset='utf-8'>"
        f"<title>Rapport QAPilot-AI</title><style>{css}</style></head>"
        f"<body>{''.join(page)}</body></html>",
        encoding="utf-8",
    )
    print(f"Rapport écrit : {OUT / 'report.md'} et {OUT / 'report.html'}")


if __name__ == "__main__":
    main()
