import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
docs = list((ROOT / "docs").rglob("*.md"))

patterns = {
    "CL": r"CL-\d{4}",
    "INV": r"INV-\d{4}",
    "OQ": r"OQ-\d{4}",
    "PP": r"PP-\d{4}",
    "REF": r"REF-\d{4}",
    "SEED": r"SEED-\d{4}",
    "LX": r"LX-\d{4}",
    "MV": r"MV-\d{4}",
}

for prefix, pat in patterns.items():
    found = []
    for p in docs:
        text = p.read_text(encoding="utf-8")
        found.extend(re.findall(pat, text))
    seen = set()
    dups = []
    for item in found:
        if item in seen:
            dups.append(item)
        seen.add(item)
    # duplicate mentions are allowed in prose, but registry IDs must exist at least once somewhere
    if prefix in {"CL","INV","OQ","PP","LX","MV"} and not found:
        print(f"missing at least one {prefix} id")
        sys.exit(1)

print("check_registry_ids: OK")
