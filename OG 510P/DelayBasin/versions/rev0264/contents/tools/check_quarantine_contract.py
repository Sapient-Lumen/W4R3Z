import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/90-quarantine/wild-speculations-2026-03-08.md"
text = DOC.read_text(encoding="utf-8")
pattern = re.compile(
    r"(^## QWS-\d{4}.*?)(?=^## QWS-\d{4}|\Z)",
    re.MULTILINE | re.DOTALL,
)
required = [
    "### Claim",
    "### What follows if true",
    "### What would count against it",
    "### Why it stays quarantined",
]
for match in pattern.finditer(text):
    block = match.group(1)
    missing = [item for item in required if item not in block]
    if missing:
        header = block.splitlines()[0]
        print(f"quarantine contract missing in {header}: {', '.join(missing)}")
        sys.exit(1)
print("check_quarantine_contract: OK")
