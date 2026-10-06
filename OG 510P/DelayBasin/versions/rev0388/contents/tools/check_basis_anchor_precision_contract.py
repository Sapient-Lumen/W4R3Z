import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/basis-witnesses-expected-head-guards-and-session-honesty-bridges.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
CONTRACT = ROOT / "docs/20-constitution/revision-receipt-contract.md"
RECEIPT = ROOT / "REVISION-RECEIPT.json"
VOCAB = ROOT / "WITNESS-VOCABULARY.json"

for path in (DOC, RUNBOOK, PROMPTS, CONTRACT, RECEIPT, VOCAB):
    if not path.exists():
        raise SystemExit(f"missing required basis-anchor-precision surface: {path}")

phrase = "basis-anchor precision / direct-underlier vs underlier-plus-wrapper vs wrapper-routed vs packet-only posture"
omission = "basis-omission basis / why stronger underliers were not reread"
if phrase not in DOC.read_text(encoding="utf-8") or omission not in DOC.read_text(encoding="utf-8"):
    raise SystemExit("basis method note missing basis-anchor precision or omission-basis guidance")
runbook = RUNBOOK.read_text(encoding="utf-8")
if "basis-anchor precision" not in runbook or "omission basis" not in runbook:
    raise SystemExit("runbook missing basis-anchor precision guidance")
prompt_text = PROMPTS.read_text(encoding="utf-8")
if phrase not in prompt_text or omission not in prompt_text:
    raise SystemExit("prompt pairs missing basis-anchor precision ratchet")
contract = CONTRACT.read_text(encoding="utf-8")
if "basis_anchor_precision" not in contract or "basis_omission_basis" not in contract:
    raise SystemExit("revision-receipt contract missing basis-anchor precision fields")

receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
basis = receipt.get("basis_witness", {})
for key in ["basis_anchor_precision", "basis_omission_basis"]:
    if key not in basis:
        raise SystemExit(f"receipt basis_witness missing key: {key}")
if not isinstance(basis.get("basis_omission_basis"), str) or not basis.get("basis_omission_basis").strip():
    raise SystemExit("receipt basis_witness.basis_omission_basis must be a non-empty string")

vocab = json.loads(VOCAB.read_text(encoding="utf-8"))
family = vocab.get("families", {}).get("basis_anchor_precision")
if not isinstance(family, dict):
    raise SystemExit("WITNESS-VOCABULARY missing basis_anchor_precision family")
expected = ["direct-underlier", "underlier-plus-wrapper", "wrapper-routed", "packet-only"]
if family.get("allowed") != expected:
    raise SystemExit("WITNESS-VOCABULARY basis_anchor_precision allowed tokens changed")
if "REVISION-RECEIPT.json" not in family.get("surfaces", []):
    raise SystemExit("WITNESS-VOCABULARY basis_anchor_precision must govern REVISION-RECEIPT.json")
if basis.get("basis_anchor_precision") not in family["allowed"]:
    raise SystemExit("receipt basis_witness.basis_anchor_precision invalid")

print("check_basis_anchor_precision_contract: OK")
