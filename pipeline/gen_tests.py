import json
import re
import sys
import time
from pathlib import Path

from pydantic import ValidationError

from pipeline.llm_client import complete
from schemas.models import CaseList, GeneratedTest

PROMPT_VERSION = "v2"
SYSTEM = Path(f"prompts/{PROMPT_VERSION}/gen_tests_api.md").read_text(encoding="utf-8")
NOTES = Path("spec/api_notes.md").read_text(encoding="utf-8")
GOLD = "\n\n".join(
    p.read_text(encoding="utf-8") for p in sorted(Path("tests/gold").glob("test_api_*.py"))
)
OUT = Path("tests/api")


def extract_code(raw: str) -> str:
    m = re.search(r"```(?:python)?\s*\n(.*?)```", raw, re.S)
    return (m.group(1) if m else raw).strip() + "\n"


def generate(case_json: str) -> str:
    user = f"## Cas de test\n{case_json}\n\n## Notes API\n{NOTES}\n\n## Exemples\n{GOLD}"
    error = ""
    for _ in range(3):
        prompt = (
            user
            if not error
            else f"{user}\n\nRéponse précédente invalide : {error}\nRenvoie uniquement un bloc ```python."
        )
        raw = complete(SYSTEM, prompt, PROMPT_VERSION, max_tokens=8000, json_mode=False)
        code = extract_code(raw)
        try:
            return GeneratedTest.model_validate({"code": code}).code
        except ValidationError as e:
            error = str(e)[:400]
    raise RuntimeError(f"échec après 3 essais ({error})")


def main(only: list[str]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for f in sorted(Path("cases").glob("REQ-*.json")):
        if only and f.stem not in only:
            continue
        cases = CaseList.model_validate(json.loads(f.read_text(encoding="utf-8")))
        for c in cases.cases:
            if c.layer != "API":
                continue
            code = generate(c.model_dump_json(indent=2))
            (OUT / f"test_{c.id.lower().replace('-', '_')}.py").write_text(code, encoding="utf-8")
            print(f"{c.id} -> tests/api")
            time.sleep(3)


if __name__ == "__main__":
    main(sys.argv[1:])
