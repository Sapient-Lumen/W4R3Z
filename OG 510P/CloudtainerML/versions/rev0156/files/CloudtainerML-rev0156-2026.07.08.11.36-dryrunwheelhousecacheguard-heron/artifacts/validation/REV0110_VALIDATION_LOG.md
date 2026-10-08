# Validation log — REV0110

Promotion allowed: `false`

## Commands

### `python3 tools/revision_metadata_coherence_audit.py`
- returncode: `0`
```
{
  "status": "pass",
  "errors": [],
  "warnings": []
}
```

### `python3 tools/public_trace_evaluation_verdict_audit.py`
- returncode: `0`
```
{
  "status": "pass_with_blockers",
  "verdict": "blocked_no_trace_bundle",
  "receipt": "artifacts/probe-results/REV0110_PUBLIC_TRACE_EVALUATION_RECEIPT.json",
  "errors": [],
  "blockers": [
    "real_public_trace_npz_missing",
    "real_public_trace_provenance_missing",
    "capture_must_complete_before_selector_evaluation",
    "evaluation_receipt_emitted_but_not_accepted"
  ]
}
```

### `python3 tools/public_trace_evaluation_receipt_audit.py`
- returncode: `0`
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

### `python3 tools/public_trace_selector_entry_gate.py`
- returncode: `0`
```
{
  "status": "pass_with_blockers",
  "verdict": "selector_entry_blocked_until_accepted_receipt",
  "selector_entry_receipt": "artifacts/probe-results/REV0110_PUBLIC_TRACE_SELECTOR_ENTRY_RECEIPT.json",
  "errors": [],
  "blockers": [
    "evaluation_receipt_not_accepted_for_selector_entry"
  ]
}
```

### `python3 tools/public_trace_receipt_relocation_audit.py`
- returncode: `0`
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

### `python3 tools/public_trace_selector_entry_receipt_audit.py`
- returncode: `0`
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

### `python3 tools/public_trace_selector_receipt_replay_gate.py`
- returncode: `0`
```
{
  "status": "pass_with_blockers",
  "verdict": "selector_receipt_replay_blocked_until_selector_entry_allowed",
  "errors": [],
  "blockers": [
    "selector_entry_receipt_does_not_open_selector_entry"
  ]
}
```

### `python3 tools/public_trace_selector_receipt_replay_audit.py`
- returncode: `0`
```
{
  "status": "pass_with_blockers",
  "case_results": {
    "selector_gate_fixture_opened": true,
    "replay_original_selector_receipt_passes": true,
    "replay_relocated_with_overrides_passes": true,
    "replay_tampered_trace_blocks": true,
    "forged_selector_subject_set_blocks": true,
    "forged_selector_tool_hash_blocks": true,
    "default_selector_receipt_not_fixture_overwritten": true
  },
  "errors": []
}
```

### `python3 tools/public_trace_selector_entry_gate.py`
- returncode: `0`
```
{
  "status": "pass_with_blockers",
  "verdict": "selector_entry_blocked_until_accepted_receipt",
  "selector_entry_receipt": "artifacts/probe-results/REV0110_PUBLIC_TRACE_SELECTOR_ENTRY_RECEIPT.json",
  "errors": [],
  "blockers": [
    "evaluation_receipt_not_accepted_for_selector_entry"
  ]
}
```

### `python3 tools/public_trace_selector_receipt_replay_gate.py`
- returncode: `0`
```
{
  "status": "pass_with_blockers",
  "verdict": "selector_receipt_replay_blocked_until_selector_entry_allowed",
  "errors": [],
  "blockers": [
    "selector_entry_receipt_does_not_open_selector_entry"
  ]
}
```

