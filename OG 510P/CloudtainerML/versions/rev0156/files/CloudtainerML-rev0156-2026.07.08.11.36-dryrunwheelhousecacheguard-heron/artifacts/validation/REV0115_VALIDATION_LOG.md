# Validation log — REV0115

Status: `pass_with_blockers`  
Validation status: `pass_no_write_and_checksum`  
Promotion allowed: `false`

## What was checked

- Cold-reviewer verification was run with `--no-write` and returned `pass_with_blockers`.
- Standalone toolpack verification was run with `--no-write` and returned `pass_with_blockers`.
- A file-tree mutation probe found no added, removed, or changed files after those no-write runs.
- The final package protocol regenerates the manifest/checksums, runs smoke validation, reruns no-write checks, then reruns smoke validation without changing package files.

## Why the final smoke output is not embedded

Embedding the final smoke output after checksum regeneration would change this file and invalidate the just-checked hashes. The final smoke command is therefore an external verification step against fixed package content.

## Remaining blockers

- `real_public_tinyllama_trace_npz_and_provenance_missing`
- `actual_evaluation_receipt_missing`
- `actual_selector_entry_receipt_missing`
- `named_hardware_timing_missing`
- `promotion_still_forbidden`
