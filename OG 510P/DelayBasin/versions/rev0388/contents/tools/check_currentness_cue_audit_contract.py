import json
import pathlib

from currentness_cue_audit_lib import build_currentness_cue_audit, render_currentness_cue_audit_md

ROOT = pathlib.Path(__file__).resolve().parents[1]
AUDIT = ROOT / "CURRENTNESS-CUE-AUDIT.json"
GUIDE = ROOT / "docs/00-meta/currentness-cue-audit.md"
actual = json.loads(AUDIT.read_text(encoding="utf-8"))
expected = build_currentness_cue_audit(ROOT)
if actual != expected:
    raise SystemExit("CURRENTNESS-CUE-AUDIT.json drifted from generated currentness cue audit")
if expected.get("counts", {}).get("failures") != 0 or expected.get("failures"):
    raise SystemExit("CURRENTNESS-CUE-AUDIT has failing currentness cues")
guide = GUIDE.read_text(encoding="utf-8")
expected_guide = render_currentness_cue_audit_md(expected)
if guide != expected_guide:
    raise SystemExit("docs/00-meta/currentness-cue-audit.md drifted from generated audit guide")
for bad in ["currentness-cue-court", "latest-head-tribunal", "status-sovereign", "bundle-revision-notary", "recency-court", "landing-cue-authority", "green-lint-currentness-waiver", "current-key-senate"]:
    if bad not in actual.get("non_claim", "") or bad not in guide:
        raise SystemExit(f"currentness cue audit missing non-claim {bad}")
print("check_currentness_cue_audit_contract: OK")
