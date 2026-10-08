# rev0126 transition boundary verifier

rev0126 audits the seam left after the transition checkpoint seal: callers could inspect `TransitionResult::checkpoint_before`, `TransitionResult::checkpoint_after`, and `transition_result_matches_receipt(...)`, but they still had to reassemble the full proposal/adoption verification by hand.

The new public `verify_transition_result_boundary(...)` verifier binds one immediate transition result to three things at once:

- the proposal `GameState` through `StateCheckpointSeal checkpoint_before`;
- the adopted or unchanged after `GameState` through `StateCheckpointSeal checkpoint_after`;
- for committed transitions, the latest causal `ActionReceiptRecord` through `transition_result_matches_receipt(...)` and `causal_receipt_hash`.

For `NeedChoice`, the verifier requires stable checkpoints, unchanged StateCore/journal/receipt counts, no staged commit sentinels, no causal receipt, and a non-empty offered action surface. For `Rejected`, it requires the nonmutating rejection contract plus zero causal receipt identity. For `Committed`, it requires `committed_with_atomic_adoption_guard()`, the adopted state's action-receipt count to match the transition result, the latest receipt index/hash to match `causal_receipt_index` / `causal_receipt_hash`, and the receipt/result verifier to accept the pair.

This is intentionally still a verifier seam, not a new persisted trace format. `ActionTrace.v16`, `ReplayArtifactManifest.v2`, and `StateCheckpointSeal.v2` remain unchanged. The mission-level effect is that branch/search/agent callers now have one public function for the trusted-transition boundary: authoritative pre-state plus explicit choice plus resulting post-state must all match the typed evidence before a caller treats the transition as trusted.
