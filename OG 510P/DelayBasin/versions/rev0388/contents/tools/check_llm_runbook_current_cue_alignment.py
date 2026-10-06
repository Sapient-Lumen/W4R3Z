import json
import pathlib

from hot_current_supports_lib import HotCurrentSupportsError, parse_current_additions, validate_hot_current_supports

ROOT = pathlib.Path(__file__).resolve().parents[1]
receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
runbook = (ROOT / "docs/00-meta/llm-runbook.md").read_text(encoding="utf-8")
rev = receipt["revision"]
heading = f"### {rev} current reentry cue"
if runbook.count(heading) != 1:
    raise SystemExit(f"llm runbook must contain exactly one current cue heading {heading}")
section = runbook.split(heading, 1)[1].split("\n### ", 1)[0]

try:
    expected = validate_hot_current_supports(ROOT, receipt)
except HotCurrentSupportsError as exc:
    raise SystemExit(str(exc)) from exc

prefix = "Current additions: "
current_lines = [line for line in section.splitlines() if prefix in line]
if len(current_lines) != 1:
    raise SystemExit(
        f"llm runbook current cue must contain exactly one Current additions field, found {len(current_lines)}"
    )
raw_additions = current_lines[0].split(prefix, 1)[1].strip()
try:
    observed = parse_current_additions(raw_additions)
except HotCurrentSupportsError as exc:
    raise SystemExit(f"llm runbook current cue: {exc}") from exc
if observed != expected:
    raise SystemExit("llm runbook current additions differ from receipt hot_current_supports")

needles = [
    receipt["packaged_bundle_filename"],
    receipt["current_method_surface"],
    receipt["current_witness_slot"]["contract_surface"],
    "tools/check_current_witness_receipt_slot.py",
    receipt["resolved_question"],
    receipt["next_open_question"],
    "VALIDATION-INDEX.json",
    "docs/00-meta/validation-index.md",
    "FRONTIER-BACKLOG.json",
    "LEDGER-AUDIT.json",
    "CANARY-PROTOCOL.json",
]
for needle in needles:
    if needle not in section:
        raise SystemExit(f"llm runbook current cue missing {needle}")
for bad in [
    "continuation-review-court",
    "canary-authority-board",
    "minimality-certification-tribunal",
    "ledger-review-court",
    "ordinal-succession-senate",
]:
    if bad not in section:
        raise SystemExit(f"llm runbook current cue missing excluded non-take {bad}")
if "Derivative aids remain non-canon" not in section:
    raise SystemExit("llm runbook current cue missing derivative aid warning")
print("check_llm_runbook_current_cue_alignment: OK")
