import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
vocab = json.loads((ROOT / "WITNESS-VOCABULARY.json").read_text(encoding="utf-8"))
handles = json.loads((ROOT / "WITNESS-FAMILY-HANDLES.json").read_text(encoding="utf-8"))
method = (ROOT / "docs/10-method/canary-evidence-calibration-witnesses.md").read_text(encoding="utf-8")
protocol = json.loads((ROOT / "CANARY-PROTOCOL.json").read_text(encoding="utf-8"))
ledger_audit = json.loads((ROOT / "LEDGER-AUDIT.json").read_text(encoding="utf-8"))
assays = json.loads((ROOT / "SELF-SUFFICIENCY-LEDGER.json").read_text(encoding="utf-8"))["items"]

if receipt.get("canary_evidence_witness", {}).get("selected_token") != "mixed-canary-evidence":
    raise SystemExit("canary-evidence selected token drifted")
family = vocab.get("families", {}).get("canary_evidence_state")
if not family:
    raise SystemExit("WITNESS-VOCABULARY missing canary_evidence_state")
expected_surfaces = ["WITNESS-VOCABULARY.json", "REVISION-RECEIPT.json", "docs/10-method/canary-evidence-calibration-witnesses.md"]
if family.get("surfaces") != expected_surfaces:
    raise SystemExit("canary-evidence family surfaces drifted")
for token in ["baseline-failure-detected", "packet-fit-sufficient", "negative-canary-clean", "differential-gain-observed", "evidence-weighted-not-authority", "ledger-audited", "tail-ordinal-guarded", "mixed-canary-evidence"]:
    if token not in family.get("allowed", []) or token not in method:
        raise SystemExit(f"missing canary-evidence token {token}")
for bad in ["continuation-review-court", "canary-authority-board", "minimality-certification-tribunal", "scorecard-canonization", "ledger-review-court", "ordinal-succession-senate", "behavioral-eval-sovereign", "self-sufficiency-notary"]:
    if bad not in family.get("excluded_synonyms", []) or bad not in method or bad not in protocol.get("non_claim", "") + " " + " ".join(protocol.get("forbidden_conclusions", [])):
        raise SystemExit(f"missing canary-evidence excluded synonym {bad}")
row = next((row for row in handles.get("families", []) if row.get("handle") == "WVF-0124"), None)
if not row or row.get("canonical_family") != "canary_evidence_state":
    raise SystemExit("WITNESS-FAMILY-HANDLES missing WVF-0124")
if protocol.get("governing_method") != "docs/10-method/canary-evidence-calibration-witnesses.md" or protocol.get("witness_family") != "canary_evidence_state":
    raise SystemExit("CANARY-PROTOCOL canary method/family drifted")
if ledger_audit.get("revision") != receipt.get("revision") or not ledger_audit.get("ledgers"):
    raise SystemExit("LEDGER-AUDIT is missing or stale")
if not any(row.get("id") == "SA-0015" and row.get("frontier_id") == "OQ-0220" for row in assays):
    raise SystemExit("self-sufficiency ledger must retain SA-0015 canary-evidence assay")
print("check_canary_evidence_witness_contract: OK")
