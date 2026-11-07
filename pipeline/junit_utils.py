import xml.etree.ElementTree as ET
from pathlib import Path

BLOCKING = Path("reports/junit.xml")
DEFECTS = Path("reports/junit_defects.xml")


def parse_junit(path: Path, source: str) -> list[dict]:
    """Retourne un dict par test : tc, test, durée, statut, message, source."""
    if not path.exists():
        return []
    tests = []
    for case in ET.parse(path).getroot().iter("testcase"):
        props = {p.get("name"): p.get("value") for p in case.iter("property")}
        status, message = "passed", ""
        for child in case:
            if child.tag in ("failure", "error"):
                status = "failed"
                message = (child.get("message") or "").split("\n")[0]
            elif child.tag == "skipped":
                xfail = child.get("type") == "pytest.xfail"
                status = "xfail" if xfail else "skipped"
                message = child.get("message") or ""
        module = (case.get("classname") or "").split(".")[-1]
        tests.append(
            {
                "tc": props.get("tc"),
                "test": f"{module}::{case.get('name')}",
                "duration": float(case.get("time") or 0),
                "status": status,
                "message": message,
                "source": source,
            }
        )
    return tests


def load_all() -> tuple[list[dict], list[dict]]:
    return parse_junit(BLOCKING, "blocking"), parse_junit(DEFECTS, "defects")
