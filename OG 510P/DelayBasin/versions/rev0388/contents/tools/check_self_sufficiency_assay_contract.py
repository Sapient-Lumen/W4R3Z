import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
ledger = json.loads((ROOT / "SELF-SUFFICIENCY-LEDGER.json").read_text(encoding="utf-8"))
receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
latest = ledger.get("items", [])[-1]
if latest.get("revision") != receipt.get("revision"):
    raise SystemExit("latest self-sufficiency assay row revision drifted")
if latest.get("assay_state") != "scored-canary":
    raise SystemExit("latest self-sufficiency assay must be scored-canary")
for key in ["scorecard", "negative_canaries", "packet_tests"]:
    if not latest.get(key):
        raise SystemExit(f"latest self-sufficiency assay missing {key}")
if len(latest.get("packet_tests", [])) < 4:
    raise SystemExit("self-sufficiency assay needs baseline, landing, compact, and full archive packet tests")
if len(latest.get("negative_canaries", [])) < 6:
    raise SystemExit("self-sufficiency assay negative canaries too thin")
canon = set(receipt.get("canon_additions", []))
seen = set()
for test in latest.get("packet_tests", []):
    seen.update(test.get("surfaces", []))
    if "observed" not in test or "score" not in test:
        raise SystemExit(f"packet test lacks observed score: {test.get('id')}")
if not canon.intersection(seen):
    raise SystemExit("self-sufficiency assay does not exercise a current canon addition")
print("check_self_sufficiency_assay_contract: OK")
