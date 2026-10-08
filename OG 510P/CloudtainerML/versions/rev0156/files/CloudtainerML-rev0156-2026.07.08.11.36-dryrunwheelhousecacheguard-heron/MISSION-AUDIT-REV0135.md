# Mission audit — REV0136

Package: `CloudtainerML-rev0136-2026.07.07.21.08-receiptchainreplay-mink`  
Status: `pass_with_expected_environment_blockers`  
Promotion allowed: `false`

## What changed

Rev0136 closes a downstream evidence-chain gap. Rev0134 made the public-trace verifier require loader binding and the pinned `model.safetensors` digest, but downstream receipts could still compress that into a single acceptance boolean. This revision adds `public_trace_downstream_identity_receipt_v1`: a compact `trace_identity_sha256` over the selected local snapshot path, verified weight digest, prompt manifest digest, tokenization/generation settings, cache contract, and trace hash. The evaluation receipt emits it, selector-entry requires it, replay cross-checks it, and the handoff builder/gate carry it.

## Risk addressed

The riskiest next failure was not another missing registry field; it was downstream drift. A future trace could pass the acceptance gate and then be moved into selector or handoff artifacts without the reviewer being able to prove that the same selected digest-verified snapshot and prompt/generation contract survived. This revision makes that identity part of the receipt chain.

## Concrete refactor/audit work

- Exposed loader-binding fields in the verifier manifest summary so receipt builders can summarize them without reparsing provenance manually.
- Added trace identity summary logic to `tools/public_trace_evaluation_verdict_audit.py`.
- Added selector receipt identity enforcement in `tools/public_trace_selector_entry_gate.py`.
- Added selector/evaluation identity replay checks in `tools/public_trace_selector_receipt_replay_gate.py`.
- Added handoff manifest identity-chain binding in `tools/public_trace_handoff_builder.py` and `tools/public_trace_handoff_archive_gate.py`.
- Added `tools/public_trace_downstream_identity_receipt_audit.py` and smoke coverage.

## Online grounding

Hugging Face local/offline execution and snapshot-download docs make path/digest identity a real runtime concern, because cache location and resolution can vary by environment. SLSA provenance and in-toto link attestations support the same design pressure: downstream consumers need digest-bound subjects/materials, not just a statement that an upstream verifier accepted something.

## Still blocked here

- No complete digest-verified TinyLlama snapshot in this cloudtainer.
- `transformers` runtime remains unavailable here.
- No real public trace, selector/evaluation receipt chain, handoff archive, or named-hardware timing has been produced.

## Validation run plan

The static/audit/smoke lane should pass. Strict capture-start preflight should remain `blocked_here` in this cloudtainer until the local snapshot and runtime are supplied.
