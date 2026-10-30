import json
import re
import time
from pathlib import Path

from pydantic import ValidationError

from pipeline.llm_client import complete
from schemas.models import CaseList

PROMPT_VERSION = "v1"
SYSTEM = Path(f"prompts/{PROMPT_VERSION}/gen_cases.md").read_text(encoding="utf-8")
API_NOTES = Path("spec/api_notes.md")
notes = API_NOTES.read_text(encoding="utf-8") if API_NOTES.exists() else "(aucune note)"


def clean(text: str) -> str:
    return re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())


def generate(req_id: str, req_text: str) -> CaseList:
    user = f"## Exigence\n{req_text}\n\n## Notes API\n{notes}"
    error = ""
    for _ in range(3):
        prompt = user if not error else (
            f"{user}\n\nTa réponse précédente était invalide : {error}\n"
            "Corrige et renvoie uniquement le JSON."
        )
        raw = complete(SYSTEM, prompt, PROMPT_VERSION)
        try:
            cases = CaseList.model_validate(json.loads(clean(raw)))
            for i, c in enumerate(cases.cases, 1):
                c.requirement_id = req_id
                c.id = f"TC-{req_id[4:]}-{i:02d}"
            return cases
        except (json.JSONDecodeError, ValidationError) as e:
            error = str(e)[:500]
    raise RuntimeError(f"{req_id} : échec après 3 essais ({error})")


def main() -> None:
    Path("cases").mkdir(exist_ok=True)
    for f in sorted(Path("requirements").glob("REQ-*.md")):
        req_id = f.stem
        cases = generate(req_id, f.read_text(encoding="utf-8"))
        out = Path("cases") / f"{req_id}.json"
        out.write_text(cases.model_dump_json(indent=2), encoding="utf-8")
        print(f"{req_id} : {len(cases.cases)} cas")
        time.sleep(3)


if __name__ == "__main__":
    main()
