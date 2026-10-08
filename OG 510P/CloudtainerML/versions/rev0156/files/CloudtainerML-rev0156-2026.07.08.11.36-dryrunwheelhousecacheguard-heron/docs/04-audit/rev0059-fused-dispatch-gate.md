# rev0059 fused dispatch gate

## Why this revision exists

rev0058 showed that a materialized score-histogram path can look fast on a native CPU row proxy, while a materialization-free streaming path avoids score storage but pays QK recompute/schedule tax. rev0059 turns that into an explicit dispatch/claim gate.

The purpose is to prevent three overclaims:

1. treating global score materialization as fused sparse-attention evidence;
2. treating value-read savings as a speed win when the no-score-storage schedule is slower;
3. treating near-dense selected sets as sparse wins.

## What changed

`experiments/fused_dispatch_gate/fused_dispatch_gate.py` consumes the measured `REV0058_FUSED_STREAMING_SCHEDULE_NATIVE.json` rows and evaluates four policies:

- `speed_only_materialized_negative_control`
- `score_storage_allowed_sparse_cpu_gate`
- `streaming_no_storage_negative_control`
- `strict_materialization_free_deployable_gate`

The strict gate requires quality, speedup, no global score storage, non-near-dense value reads, and no QK recompute blowup. It chooses no sparse regimes in the current evidence.

## Result

The only score-storage-allowed sparse CPU regime is `peaked_low_support`. The strict materialization-free gate falls back to dense everywhere. The speed-only negative control falsely chooses near-dense `medium_support` and `broad_high_entropy`, which is now audited as a failure mode rather than a success.

## Status

Promotion remains blocked by missing public/pretrained traces and missing GPU/fused-kernel timing.
