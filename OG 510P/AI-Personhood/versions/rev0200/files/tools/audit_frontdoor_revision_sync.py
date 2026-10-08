import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
REV_NUM = int(REV.replace("rev", ""))


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

# Front doors must name the current rev in the title and this-revision block.
for rel in ["README.md", "START_HERE.md"]:
    text = (ROOT / rel).read_text(encoding="utf-8")
    first = text[:2500]
    if REV not in first:
        raise SystemExit(f"{rel} front-door opening does not mention {REV}")
    if "## This revision" in text:
        block = text.split("## This revision", 1)[1][:2200]
        stale = sorted({m.group(0) for m in re.finditer(r"rev(0[0-9]{3})", block) if int(m.group(1)) < REV_NUM})
        allowed = {f"rev{REV_NUM-1:04d}"}
        unexpected = [r for r in stale if r not in allowed]
        if unexpected:
            raise SystemExit(f"{rel} this-revision block contains unexpected stale revision refs: {unexpected}")

status = load("SURFACE-STATUS.json")
receipt = load("REVISION-RECEIPT.json")
if status.get("revision") != REV:
    raise SystemExit("SURFACE-STATUS revision mismatch")
if receipt.get("revision") != REV:
    raise SystemExit("REVISION-RECEIPT revision mismatch")
read_first = status.get("operational_head", {}).get("read_first")
if not read_first or not (ROOT / read_first).exists():
    raise SystemExit(f"read_first missing or absent: {read_first}")
if read_first not in (ROOT / "START_HERE.md").read_text(encoding="utf-8"):
    raise SystemExit("START_HERE does not include operational read_first surface")

for stem in ["schema-fixture-domain-registry", "canon-surface-catalog", "doctrine-dependency-map", "rights-domain-coverage-map", "research-tail-compaction-map"]:
    path = ROOT / "examples" / f"{stem}-{REV}.json"
    if not path.exists():
        raise SystemExit(f"active map missing: {path.relative_to(ROOT)}")

# The active status new surfaces should all be indexed and physically present.
index = (ROOT / "ARCHIVE_INDEX.md").read_text(encoding="utf-8")
for rel in status.get("new_surfaces", []):
    if not (ROOT / rel).exists():
        raise SystemExit(f"status new surface missing: {rel}")
    if rel not in index:
        raise SystemExit(f"status new surface absent from archive index: {rel}")

print("audit_frontdoor_revision_sync: OK")
