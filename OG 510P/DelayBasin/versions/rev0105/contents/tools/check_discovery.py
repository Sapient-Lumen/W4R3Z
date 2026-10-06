import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
INDEX = DOCS / "README.md"

index_text = INDEX.read_text(encoding="utf-8")
linked = set(re.findall(r"\(([^)]+\.md)\)", index_text))

expected = {
    str(p.relative_to(DOCS)).replace("\\", "/")
    for p in DOCS.rglob("*.md")
    if p.name != "README.md"
}

missing = sorted(expected - linked)
if missing:
    print("docs/README.md is missing links for:")
    for item in missing:
        print(f"  - {item}")
    sys.exit(1)

print("check_discovery: OK")
