# Public trace evaluation verdict contract — REV0106

Status: `active_blocker_gate`  
Promotion allowed: `false`

This contract adds a hard line between three states:

1. `blocked_no_trace_bundle`: no NPZ/provenance pair exists; do not evaluate.
2. `trace_bundle_rejected_before_evaluation`: a pair exists but the public verifier rejects it; do not evaluate.
3. `accepted_for_selector_evaluation_not_promotion`: the pair passes the public verifier and may enter selector/cost evaluation, but still cannot promote without named-hardware sparse-vs-dense timing.

The contract is based on current HF generation/cache surfaces and PyTorch determinism/timing semantics reviewed in `artifacts/research/REV0106_ONLINE_RESEARCH_NOTES.md`.
