# rev0127 — transition boundary seal

rev0127 audits the seam left after the transition boundary verifier. rev0126 gave callers a single `verify_transition_result_boundary(...)` composition point, but the verified `TransitionResult` itself still lacked a compact, durable seal saying "this exact result surface is the one that was checked."

This revision adds `kTransitionBoundarySealSchemaVersion`, `TransitionResult::transition_boundary_schema_version`, `TransitionResult::transition_boundary_hash`, public `transition_result_boundary_hash(...)`, `has_transition_boundary_seal()`, and `committed_with_transition_boundary_seal()`. `commit_action_transition(...)` and `pending_transition_for_player(...)` call `seal_transition_result_boundary(...)` only after the final status, reason, checkpoint, choice, page/queue proof, receipt, journal, and staging fields have settled.

The boundary seal deliberately hashes the semantic evidence surface rather than private object identity:

- status and reason;
- canonical selected-action hash and schema;
- local `ChoiceRequest` and APNAP `ChoiceRequestQueue` proof summaries;
- page-location and queue-location proof details;
- before/after `StateCheckpointSeal` fields;
- StateCore, journal, post-action/pre-receipt, action-receipt, and event-sequence scalars;
- causal receipt index/hash/schema;
- staging/adoption guard sentinels.

`verify_transition_result_boundary(...)` now starts by requiring `has_transition_boundary_seal()` and by recomputing `transition_result_boundary_hash(result)`. A stale or tampered result surface is rejected before the verifier reaches the status-specific checkpoint and receipt checks. A maliciously recomputed seal still cannot bypass the older guards: committed results must continue to match the adopted latest `ActionReceiptRecord` through `transition_result_matches_receipt(...)` and the causal receipt hash.

`test_transition_result_boundary_seal_hashes_committed_pending_and_rejected` covers all three statuses. It proves sealed `NeedChoice`, `Rejected`, and `Committed` results recompute exactly, stale seals reject after surface drift, and a resealed page-location mismatch still fails receipt verification. `ActionTrace.v16`, `StateCheckpointSeal.v2`, and `ReplayArtifactManifest.v2` remain unchanged.
