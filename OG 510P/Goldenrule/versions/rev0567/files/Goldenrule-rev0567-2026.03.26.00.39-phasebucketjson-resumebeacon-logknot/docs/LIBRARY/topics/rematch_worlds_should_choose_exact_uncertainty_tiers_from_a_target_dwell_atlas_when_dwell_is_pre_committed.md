# Rematch worlds should choose exact uncertainty tiers from a target-dwell atlas when dwell is pre-committed

## Claim
When a deployment shape already fixes the target dwell, future inheritors should start from a **target-dwell atlas** rather than from the generic uncertainty tier menu.
The saved exact certifications now imply a simple dwell-first map:
- dwell `2` is a precision-only singleton owned by exact `0.99`,
- dwell `8–18` is the strongest non-fragile exact band owned by exact `0.95`,
- dwell `19–32` is the relaxed exact suffix owned by exact `0.85`,
- dwell `3–7` is a real internal exact gap,
- and dwells below `2` or above `32` are outside the current exact menu.

## Why this matters
Most recent archive cards are requirement-first: floor thresholds, cap ladders, repair guides, and the executable oracle.
That is correct when the deployment can move dwell freely.
But many real implementors arrive with the shape already constrained by another subsystem.
In that case, the first useful question is not “what floor do I want?” but “what exact menu even survives at this dwell?”

The new atlas makes two expensive facts explicit:
- insisting on dwell `2` is **never** a cheap low-floor shortcut, because exact `0.99` is the only current row that contains it,
- and insisting on dwell `19+` hard-limits the best available exact uncertainty floor to `0.870482`, no matter how much extra cap or checkpoint budget is available.

So the archive should remember the dwell-first view directly.
It prevents wasted effort trying to “buy up” the relaxed suffix with more budget, and it prevents underestimating the real precision tax of the singleton dwell `2` mode.

## Implementor rule
- If target dwell is already fixed, consult the dwell atlas before broader retuning.
- Treat dwell `2` as precision-only and budget accordingly.
- Treat dwell `8–18` as the strongest non-fragile exact region.
- Treat dwell `19–32` as relaxed-only support that cannot be upgraded by more cap or checkpoints.
- Skip dwell `3–7` entirely unless new frontier evidence is generated.

## Pointers
- `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_target_dwell_atlas_snapshot.py`
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_target_dwell_atlas_snapshot_20260308.{md,json}`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_target_dwell_atlas.py`
- `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_oracle.py`
