import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
policy = json.loads((ROOT / "LINK-INTEGRITY-POLICY.json").read_text(encoding="utf-8"))
receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
if policy.get("revision") != receipt.get("revision"):
    raise SystemExit("LINK-INTEGRITY-POLICY revision drifted")
if policy.get("state") != "policy-only-not-live-checked":
    raise SystemExit("LINK-INTEGRITY-POLICY must not claim a live network check")
if policy.get("bibliography_surface") != "docs/00-meta/bibliography.md":
    raise SystemExit("LINK-INTEGRITY-POLICY bibliography surface drifted")
if "does not claim" not in policy.get("negative_canary", ""):
    raise SystemExit("LINK-INTEGRITY-POLICY missing negative canary")
print("check_link_integrity_policy_contract: OK")
