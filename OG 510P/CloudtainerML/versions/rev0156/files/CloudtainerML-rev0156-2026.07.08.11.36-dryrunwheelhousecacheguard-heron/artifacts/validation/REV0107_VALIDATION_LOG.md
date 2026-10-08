# Validation log — REV0107

$ python -m py_compile tools/public_trace_evaluation_verdict_audit.py tools/public_trace_evaluation_receipt_audit.py tools/public_trace_selector_entry_gate.py tools/public_trace_readiness_gate.py tools/smoke_validate.py
## stdout

## stderr

## returncode
0

---
$ python tools/public_trace_evaluation_verdict_audit.py
## stdout
{
  "status": "pass_with_blockers",
  "verdict": "blocked_no_trace_bundle",
  "receipt": "artifacts/probe-results/REV0107_PUBLIC_TRACE_EVALUATION_RECEIPT.json",
  "errors": [],
  "blockers": [
    "real_public_trace_npz_missing",
    "real_public_trace_provenance_missing",
    "capture_must_complete_before_selector_evaluation",
    "evaluation_receipt_emitted_but_not_accepted"
  ]
}

## stderr

## returncode
0

---
$ python tools/public_trace_evaluation_receipt_audit.py
## stdout
{
  "status": "pass_with_blockers",
  "case_results": {
    "missing_trace_receipt_blocks_selector_entry": true,
    "accepted_verifier_receipt_opens_selector_but_not_promotion": true
  },
  "errors": []
}

## stderr

## returncode
0

---
$ python tools/public_trace_selector_entry_gate.py
## stdout
{
  "status": "pass_with_blockers",
  "verdict": "selector_entry_blocked_until_accepted_receipt",
  "errors": [],
  "blockers": [
    "evaluation_receipt_not_accepted_for_selector_entry"
  ]
}

## stderr

## returncode
0

---
$ python tools/revision_metadata_coherence_audit.py
## stdout
{
  "status": "pass",
  "errors": [],
  "warnings": []
}

## stderr

## returncode
0

---
$ python tools/revision_metadata_coherence_audit.py
## stdout
{
  "status": "pass",
  "errors": [],
  "warnings": []
}

## stderr

## returncode
0
