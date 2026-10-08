# Mission audit — REV0136

Status: `non_promotional_forward_progress`  
Promotion allowed: `false`  
Current run alias: `artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh`

## Why this revision exists

Rev0135 made downstream receipts carry a compact selected-snapshot / prompt / generation identity. Rev0136 closes the next replay-risk seam: a selector-entry receipt could still be copied or paired with a different evaluation receipt and actual replay bundle unless the selector-entry handoff itself carried a chain digest that a cold reviewer can recompute.

## Substantive changes

- Added `public_trace_selector_entry_chain_v1`.
- `tools/public_trace_selector_entry_gate.py` now emits `selector_entry_chain_sha256` into selector-entry receipts.
- The chain digest binds:
  - accepted evaluation receipt SHA-256,
  - evaluation receipt subject-set SHA-256,
  - downstream `trace_identity_sha256`,
  - actual replay bundle subject-set SHA-256,
  - selector gate tool SHA-256.
- `tools/public_trace_selector_receipt_replay_gate.py` now recomputes the selector-entry chain digest from actual files/tools and blocks mismatches.
- `tools/public_trace_handoff_builder.py` and `tools/public_trace_handoff_archive_gate.py` now carry and replay the selector-entry chain hash in portable handoff archives.
- Added `tools/public_trace_selector_receipt_chain_binding_audit.py` and wired it into the current run wrappers and smoke checks.
- Refactored the current wrappers to remove duplicate acceptance-loader-binding audit calls.
- Corrected the current capture-start preflight invocation from the broken `--strict capture` shape to the real CLI shape: `--phase capture --strict`.

## Audit/refactor result

This revision fixes a concrete run-path bug and a concrete receipt-chain ambiguity. It does not add a new registry. The added audit is deliberately narrow: it checks that the selector-entry chain digest exists, is replayed, is carried into handoff, and is wired into the current live wrappers.

## Research applied

The online research reinforced three points:

1. Hugging Face local/offline loading only becomes reviewable when the exact local directory/snapshot is selected and recorded.
2. `snapshot_download()` and HF cache behavior distinguish repository/revision identity from arbitrary local path labels.
3. SLSA/in-toto style attestations bind decisions to subject digests and predicates; rev0136 applies that pattern to the trace/evaluation/selector handoff chain.

The supporting note is in `artifacts/research/REV0136_DOWNSTREAM_IDENTITY_RECEIPT_RESEARCH.md`.

## Still blocked here

- No complete digest-verified TinyLlama snapshot is present in this cloudtainer.
- `transformers` is still not importable here.
- No real public trace, evaluation receipt, selector-entry receipt, handoff archive, or named-hardware timing has been produced here.

## Next highest-risk work

Materialize or mount the pinned TinyLlama snapshot, verify `model.safetensors` SHA-256, run `artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh`, and let the capture/evaluation/selector/handoff chain produce real receipts. Any next code changes should be in service of that run path, not more taxonomy.
