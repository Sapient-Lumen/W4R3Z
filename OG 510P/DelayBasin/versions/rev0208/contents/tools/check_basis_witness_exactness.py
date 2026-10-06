import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/basis-witnesses-expected-head-guards-and-session-honesty-bridges.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
CONTRACT = ROOT / "docs/20-constitution/revision-receipt-contract.md"
RECEIPT = ROOT / "REVISION-RECEIPT.json"

for path in (DOC, RUNBOOK, PROMPTS, CONTRACT, RECEIPT):
    if not path.exists():
        raise SystemExit(f"missing required basis-exactness surface: {path}")

text = DOC.read_text(encoding="utf-8")
if "refusing to call a basis **current** unless the expected head and the observed reread basis still match exactly" not in text:
    raise SystemExit("basis method note missing exact-current rule")
if "the expected head and observed reread head still match exactly" not in RUNBOOK.read_text(encoding="utf-8"):
    raise SystemExit("runbook missing exact-current rule")
prompt_text = PROMPTS.read_text(encoding="utf-8")
if "use `current` only when expected and observed basis still match exactly" not in prompt_text or "never call the basis `current` when the expected and observed heads differ" not in prompt_text:
    raise SystemExit("prompt pairs missing basis exactness guidance")
if "basis_witness.basis_state` as `current` even though the expected head and observed reread head no longer match exactly" not in CONTRACT.read_text(encoding="utf-8"):
    raise SystemExit("revision-receipt contract missing basis exactness failure mode")

receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
basis = receipt.get("basis_witness", {})
if basis.get("basis_state") == "current" and basis.get("expected_head") != basis.get("observed_head"):
    raise SystemExit("basis exactness failure: current basis_state requires matching expected_head and observed_head")

print("check_basis_witness_exactness: OK")
