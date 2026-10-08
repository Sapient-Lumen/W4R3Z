# Public trace surrogate rejection audit — REV0117

Status: `pass_with_blockers`  
Verdict: `surrogate_rejection_blocked_no_real_trace`  
Promotion allowed: `false`

Negative-control audit for the live public trace lane. Once a real trace/provenance pair exists, the same verifier must accept the untouched pair but reject a tampered nonpublic/surrogate manifest, proving the lane does not silently promote diagnostic or fixture traces.

## Trace inputs

- trace NPZ: `artifacts/trace-bundles/REV0117_PUBLIC_LLAMA_POST_TRANSFORM_TRACE.npz`
- provenance JSON: `artifacts/trace-bundles/REV0117_PUBLIC_LLAMA_POST_TRANSFORM_TRACE.provenance.json`

## Blockers

- `real_public_trace_npz_or_provenance_missing`

## Errors

- none
