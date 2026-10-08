# Validation log — REV0109

Package: `CloudtainerML-rev0109-2026.07.06.16.07-selectorentryreceiptgate-kite`

## Audit commands

### `$ python tools/public_trace_evaluation_verdict_audit.py`
- return code: `0`
```
{
  "status": "pass_with_blockers",
  "verdict": "blocked_no_trace_bundle",
  "receipt": "artifacts/probe-results/REV0109_PUBLIC_TRACE_EVALUATION_RECEIPT.json",
  "errors": [],
  "blockers": [
    "real_public_trace_npz_missing",
    "real_public_trace_provenance_missing",
    "capture_must_complete_before_selector_evaluation",
    "evaluation_receipt_emitted_but_not_accepted"
  ]
}
```
### `$ python tools/public_trace_selector_entry_gate.py`
- return code: `0`
```
{
  "status": "pass_with_blockers",
  "verdict": "selector_entry_blocked_until_accepted_receipt",
  "selector_entry_receipt": "artifacts/probe-results/REV0109_PUBLIC_TRACE_SELECTOR_ENTRY_RECEIPT.json",
  "errors": [],
  "blockers": [
    "evaluation_receipt_not_accepted_for_selector_entry"
  ]
}
```
### `$ python tools/public_trace_evaluation_receipt_audit.py`
- return code: `0`
```
{
  "status": "pass_with_blockers",
  "case_results": {
    "accepted_receipt_has_subject_set": true,
    "accepted_receipt_opens_selector_but_not_promotion": true,
    "hash_mismatch_closes_selector_entry": true,
    "missing_trace_receipt_blocks_selector_entry": true
  },
  "errors": []
}
```
### `$ python tools/public_trace_receipt_relocation_audit.py`
- return code: `0`
```
{
  "status": "pass_with_blockers",
  "case_results": {
    "subject_set_stable_after_rename": true,
    "paths_differ_but_hashes_match": true,
    "selector_allows_original_matching_files": true,
    "selector_allows_relocated_matching_files": true,
    "selector_blocks_tampered_relocated_trace": true,
    "selector_blocks_v1_or_missing_subject_set": true
  },
  "errors": []
}
```
### `$ python tools/public_trace_selector_entry_receipt_audit.py`
- return code: `0`
```
{
  "status": "pass_with_blockers",
  "case_results": {
    "accepted_matching_bundle_opens_selector_entry": true,
    "selector_entry_receipt_emitted": true,
    "selector_receipt_binds_selector_gate_hash": true,
    "input_subject_set_recomputed": true,
    "relocated_matching_bundle_still_opens_selector_entry": true,
    "tampered_file_blocks_selector_entry": true,
    "forged_subject_set_blocks_selector_entry": true,
    "forged_evaluator_tool_hash_blocks_selector_entry": true
  },
  "errors": []
}
```
### `$ python tools/revision_metadata_coherence_audit.py`
- return code: `0`
```
{
  "status": "pass",
  "errors": [],
  "warnings": []
}
```
## Pre-check smoke before checksums
```
{
  "status": "fail",
  "revision": "rev0109",
  "revision_kind": "public_trace_relocation_safe_receipt_and_metadata_counter_fix",
  "errors": [
    "missing required file: artifacts/validation/REV0109_VALIDATION_LOG.md",
    "missing required file: CHECKSUMS.sha256"
  ],
  "warnings": []
}
```

## Metadata coherence rerun after count update
```
{
  "status": "pass",
  "errors": [],
  "warnings": []
}
```

## Final smoke validate
```
{
  "status": "pass",
  "revision": "rev0109",
  "revision_kind": "public_trace_relocation_safe_receipt_and_metadata_counter_fix",
  "errors": [],
  "warnings": []
}
```

## Final smoke validate after checksum refresh
```
{
  "status": "pass",
  "revision": "rev0109",
  "revision_kind": "public_trace_relocation_safe_receipt_and_metadata_counter_fix",
  "errors": [],
  "warnings": []
}
```
