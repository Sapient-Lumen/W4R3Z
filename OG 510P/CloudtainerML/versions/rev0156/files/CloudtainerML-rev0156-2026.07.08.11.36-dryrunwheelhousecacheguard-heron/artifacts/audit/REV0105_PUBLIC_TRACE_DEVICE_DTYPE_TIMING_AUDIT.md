# Public trace device/dtype/timing audit — REV0105

Status: `pass_with_blockers`  
Promotion allowed: `false`

This audit prevents a public trace from silently changing load dtype, device placement, or timing-clock semantics after prompt/cache/backend identity has already been pinned.

## Contract checks

- `good_runtime_contract_passes` = `True`
- `missing_resolved_dtype_rejected` = `True`
- `timing_promotion_claim_rejected` = `True`
- `implicit_dtype_rejected` = `True`

## Blockers

- `runtime_dependencies_missing_here`
- `actual_public_pretrained_trace_missing`
- `named_hardware_sparse_vs_dense_timing_missing`
