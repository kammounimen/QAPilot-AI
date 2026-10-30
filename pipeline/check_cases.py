import json
import sys
from pathlib import Path

from schemas.models import CaseList

reqs = {f.stem for f in Path("requirements").glob("REQ-*.md")}
errors, ids, titles = [], set(), set()

for req_id in sorted(reqs):
    f = Path("cases") / f"{req_id}.json"
    if not f.exists():
        errors.append(f"{req_id} : aucun cas généré")
        continue
    cases = CaseList.model_validate(json.loads(f.read_text(encoding="utf-8"))).cases
    types = {c.type for c in cases}
    if not {"nominal", "negative"} <= types:
        errors.append(f"{req_id} : il manque un cas nominal ou négatif")
    for c in cases:
        if c.id in ids:
            errors.append(f"ID en double : {c.id}")
        if c.title.lower() in titles:
            errors.append(f"Titre en double : {c.title}")
        ids.add(c.id)
        titles.add(c.title.lower())

for f in Path("cases").glob("REQ-*.json"):
    if f.stem not in reqs:
        errors.append(f"{f.name} : cas orphelin, exigence inconnue")

print(f"{len(ids)} cas pour {len(reqs)} exigences")
if errors:
    print("\n".join(errors))
    sys.exit(1)
print("OK")
