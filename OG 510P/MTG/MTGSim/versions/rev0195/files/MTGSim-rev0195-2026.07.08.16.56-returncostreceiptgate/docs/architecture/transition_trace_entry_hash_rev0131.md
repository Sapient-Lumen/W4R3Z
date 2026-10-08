# Transition trace-entry hash refactor — rev0131

rev0131 audits the implementation seam left by the transition trace handoff seal. rev0130 bound a committed `TransitionResult` to the replay-facing `ActionTraceEntry`, but `transition_result_trace_handoff_hash(...)` still carried a local copy of the trace-entry field hashing logic. That duplicate hash path could drift from `action_trace_entry_hash(...)` as the trace surface evolves.

The refactor adds public `transition_result_trace_entry_hash(...)` and makes it delegate to the canonical projection path: `action_trace_entry_from_transition_result(...)` followed by `action_trace_entry_hash(...)`. `transition_result_trace_handoff_hash(...)` now hashes that helper result instead of re-stating every `ActionTraceEntry` field. This keeps the transition handoff seal, receipt-exported trace rows, projected transition trace rows, and replay diagnostics on one hash spine.

The new regression `test_transition_trace_handoff_uses_canonical_trace_entry_hash` proves the helper equals the canonical `ActionTraceEntry` hash, that the handoff seal recomputes through the helper, and that a maliciously resealed page-location projection drift still fails the boundary verifier at the receipt/result seam.

Compatibility is intentionally narrow: `ActionTrace.v16`, `StateCheckpointSeal.v2`, `ReplayArtifactManifest.v2`, and the rev0130 handoff hash domain remain unchanged. The change removes duplicate implementation logic rather than minting a new serialized replay artifact version.

The maintained audit phrase for this seam is canonical trace-entry hash: one helper owns the projected trace-row digest used by transition and replay callers.
