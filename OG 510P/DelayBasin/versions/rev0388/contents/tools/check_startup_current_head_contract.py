import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
manifest = json.loads((ROOT / "RELEASE-MANIFEST.json").read_text(encoding="utf-8"))
expected_rev = receipt["revision"]
expected_bundle = receipt["packaged_bundle_filename"]
if manifest.get("bundle") != expected_bundle:
    raise SystemExit("startup head check requires manifest bundle to match receipt")

CURRENT_PATTERNS = (
    re.compile(r"^Latest revision:? `(?P<rev>rev\d{4})` / `(?P<bundle>DelayBasin-rev\d{4}-[^`]+\.zip)`", re.M),
    re.compile(r"^Current packaged(?: docs)? head: `(?P<rev>rev\d{4})`(?: / `(?P<bundle>DelayBasin-rev\d{4}-[^`]+\.zip)`)?", re.M),
    re.compile(r"^Current packaged docs head: `(?P<rev>rev\d{4})`", re.M),
)

for rel in ["README.md", "START_HERE.md", "docs/README.md", "AGENTS.md"]:
    text = (ROOT / rel).read_text(encoding="utf-8")
    current_lines = []
    for pattern in CURRENT_PATTERNS:
        for m in pattern.finditer(text):
            current_lines.append((m.group(0), m.groupdict().get("rev"), m.groupdict().get("bundle")))
    if not current_lines:
        raise SystemExit(f"{rel} missing current-head cue")
    for line, rev, bundle in current_lines:
        if rev != expected_rev:
            raise SystemExit(f"{rel} stale current revision cue: {line}")
        if bundle is not None and bundle != expected_bundle:
            raise SystemExit(f"{rel} stale current bundle cue: {line}")
    bundles = [b for _, _, b in current_lines if b]
    if expected_bundle not in bundles:
        raise SystemExit(f"{rel} does not name expected current bundle {expected_bundle}")

for rel in ["README.md", "START_HERE.md", "docs/README.md"]:
    text = (ROOT / rel).read_text(encoding="utf-8")
    bad = re.findall(r"^Historical latest-revision note `(?P<rev>rev\d{4})` \((?P<bundle>DelayBasin-rev\d{4}-[^)]+\.zip)\)", text, re.M)
    for rev, bundle in bad:
        if rev == expected_rev and bundle != expected_bundle:
            raise SystemExit(f"{rel} has historical latest note with current rev but stale bundle: {bundle}")

print("check_startup_current_head_contract: OK")
