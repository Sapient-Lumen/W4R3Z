# Mission audit — REV0106: verdict gate + metadata fix

## Status

`pass_with_blockers`; promotion remains false.

## Highest-risk lane worked

The riskiest unfinished work is still not another doctrine artifact; it is a real public TinyLlama prefill+cached-decode trace that can survive evaluation. Rev0106 adds a verdict gate so a trace cannot move from “captured” to “evaluable” unless the NPZ/provenance pair passes the existing public trace provenance verifier.

## Concrete defect corrected

Rev0105 still carried stale current metadata (`current_revision: rev0103`, stale primary artifacts, and stale focus labels) despite being packaged as rev0105. That is a handoff risk: an operator could follow current-looking docs while automation keys off stale revision identity. Rev0106 updates top-level metadata and hardens `revision_metadata_coherence_audit.py` and `smoke_validate.py` to catch stale `current_revision`, `evidence_revision`, and current artifact pointers.

## New execution surface

- `tools/public_trace_evaluation_verdict_audit.py` writes a machine-readable verdict:
  - `blocked_no_trace_bundle`: no NPZ/provenance pair exists.
  - `trace_bundle_rejected_before_evaluation`: a pair exists but the verifier rejects it.
  - `accepted_for_selector_evaluation_not_promotion`: the pair passes verifier checks but still needs named-hardware timing.
- `tools/public_trace_readiness_gate.py` now includes the verdict audit.
- `artifacts/capture-kit/REV0106_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh` runs the verdict gate after the real-model gate.

## Research applied

Online review of HF generation/cache docs and PyTorch reproducibility/timing docs reinforces the split between generation output, trace bundle acceptance, selector evaluation, and promotion timing. The current change encodes that split as a gate rather than prose.

## Remaining blockers

- Real public TinyLlama trace NPZ/provenance pair is still missing in this capsule.
- Exact model snapshot/runtime is still absent here.
- Named-hardware sparse-vs-dense timing remains missing.
