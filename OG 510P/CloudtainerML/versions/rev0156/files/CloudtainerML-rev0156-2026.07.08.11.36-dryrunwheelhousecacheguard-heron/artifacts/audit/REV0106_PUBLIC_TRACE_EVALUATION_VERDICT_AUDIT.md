# Public trace evaluation verdict audit — REV0106

Status: `pass_with_blockers`  
Verdict: `blocked_no_trace_bundle`  
Promotion allowed: `false`

Prevents a partial or merely captured trace bundle from entering selector/cost evaluation until the NPZ and provenance manifest pass the public trace gate verifier. Acceptance here is only an evaluation-entry verdict; named-hardware timing remains a separate promotion blocker.

## Blockers
- `real_public_trace_npz_missing`
- `real_public_trace_provenance_missing`
- `capture_must_complete_before_selector_evaluation`

## Errors
- none
