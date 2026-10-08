# rev0128 — transition boundary diagnostics

rev0128 audits the seam left after the transition boundary seal. rev0127 made `TransitionResult` self-sealing and kept the existing bool `verify_transition_result_boundary(...)` gate, but callers still only learned "false" when the boundary failed. That was enough for rejection, but weak for replay bundle localization, search-tree pruning, fuzz triage, and future agents that need to distinguish a stale result seal from a mismatched adopted state or a corrupted causal receipt.

This revision adds `TransitionBoundaryFailureKind`, `TransitionBoundaryVerifyResult`, public `check_transition_result_boundary(...)`, and `to_string(TransitionBoundaryFailureKind)`. The older bool wrapper remains compatible and now delegates to the diagnostic verifier's `passed()` result.

The diagnostic verifier reports stable first-failure kinds for the full transition boundary:

- `StatusInvalid` for impossible `TransitionStatus` values;
- `BoundarySealMissing` and `BoundarySealMismatch` for absent/stale `transition_boundary_hash` evidence;
- `CheckpointSealMismatch`, `BeforeCheckpointMismatch`, and `AfterCheckpointMismatch` for local checkpoint shape and proposal/adopted state drift;
- `NeedChoiceMutation`, `NeedChoiceMissingActions`, and `NeedChoiceCausalReceipt` for broken pure-inspection surfaces;
- `RejectedMutation` and `RejectedCausalReceipt` for broken nonmutating rejection surfaces;
- `CommittedAtomicGuardMissing` for committed results that no longer satisfy the staged adoption guard;
- `ReceiptCountMismatch`, `ReceiptMissing`, `ReceiptIndexMismatch`, `ReceiptHashMismatch`, and `ReceiptResultMismatch` for committed receipt-boundary drift.

`TransitionBoundaryVerifyResult` also echoes `expected_transition_boundary_hash`, `observed_transition_boundary_hash`, `expected_causal_receipt_hash`, `observed_causal_receipt_hash`, and `causal_receipt_index` when those values are available. That makes the diagnostic surface useful without requiring callers to recompute the hash protocol themselves.

`test_transition_boundary_diagnostics_localize_failure_kind` proves that a valid committed transition passes, a zero boundary seal reports `BoundarySealMissing`, stale surface drift reports `BoundarySealMismatch`, wrong adopted state reports `AfterCheckpointMismatch`, maliciously resealed causal receipt drift reports `ReceiptHashMismatch`, resealed receipt/result payload drift reports `ReceiptResultMismatch`, empty `NeedChoice` action lists report `NeedChoiceMissingActions`, and an invalid status reports `StatusInvalid`. `ActionTrace.v16`, `StateCheckpointSeal.v2`, and `ReplayArtifactManifest.v2` remain unchanged.
