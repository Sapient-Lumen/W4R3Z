# Validation log — REV0114

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
  "receipt": "artifacts/probe-results/REV0114_PUBLIC_TRACE_EVALUATION_RECEIPT.json",
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
  "selector_entry_receipt": "artifacts/probe-results/REV0114_PUBLIC_TRACE_SELECTOR_ENTRY_RECEIPT.json",
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

### `python3 tools/public_trace_handoff_archive_gate.py`
- returncode: `0`
```
{
  "status": "pass_with_blockers",
  "verdict": "handoff_archive_blocked_no_manifest",
  "errors": [],
  "blockers": [
    "real_public_trace_handoff_manifest_missing"
  ]
}
```

### `python3 tools/public_trace_handoff_archive_audit.py`
- returncode: `0`
```
{
  "status": "pass_with_blockers",
  "case_results": {
    "selector_entry_fixture_opened": true,
    "direct_toolpacked_handoff_gate_passes": true,
    "toolpack_subject_set_verified": true,
    "extracted_archive_gate_passes": true,
    "archive_movement_preserves_subject_sets": true,
    "tampered_extracted_trace_blocks": true,
    "path_escape_manifest_blocks": true,
    "forged_handoff_subject_set_blocks": true,
    "forged_toolpack_subject_set_blocks": true,
    "missing_toolpack_subject_blocks": true,
    "tampered_toolpack_tool_blocks": true
  },
  "errors": []
}
```

### `python3 tools/public_trace_standalone_toolpack_audit.py`
- returncode: `0`
```
{
  "status": "pass_with_blockers",
  "verdict": "standalone_toolpack_replay_verified_not_promotion",
  "errors": []
}
```

### `python3 tools/public_trace_cold_reviewer_verify_audit.py`
- returncode: `0`
```
{
  "status": "pass_with_blockers",
  "verdict": "cold_reviewer_verify_path_hardened_not_promotion",
  "case_results": {
    "direct_no_arg_gate_passes_after_move": true,
    "verify_handoff_wrapper_passes_after_move": true,
    "direct_gate_rejects_tampered_wrapper": true,
    "no_arg_gate_fails_without_root_manifest": true,
    "root_wrapper_blocks_outside_handoff": true
  },
  "errors": []
}
```

## Finalization

After this log was written, metadata counts, `FILE-MANIFEST.json`, and `CHECKSUMS.sha256` were regenerated, then smoke validation and checksum verification were run before packaging.
