# Transition trace-entry seal — rev0132

rev0132 audits the seam left after the canonical trace-entry hash refactor. `transition_result_trace_entry_hash(...)` already delegated through `action_trace_entry_from_transition_result(...)` and `action_trace_entry_hash(...)`, but a committed `TransitionResult` still forced callers to recompute that digest if they wanted to verify the replay projection directly.

The new carried surface is:

- `kActionTraceEntrySchemaVersion`;
- `TransitionResult::action_trace_entry_schema_version`;
- `TransitionResult::action_trace_entry_hash`;
- `TransitionResult::has_action_trace_entry_seal()`.

`commit_action_transition(...)` computes `result.action_trace_entry_hash = transition_result_trace_entry_hash(result)` after the staged state is adopted and before `transition_result_trace_handoff_hash(...)` and `transition_result_boundary_hash(...)` are finalized. The boundary seal therefore binds the same canonical `ActionTraceEntry` digest that replay consumers inspect, instead of leaving it as an external convention.

`check_transition_result_boundary(...)` now recomputes `expected_action_trace_entry_hash`, reports `observed_action_trace_entry_hash`, and echoes `expected_action_trace_entry_schema_version` / `observed_action_trace_entry_schema_version`. The verifier returns `TraceEntrySealMissing` if a committed result has no carried trace-entry hash and `TraceEntrySealMismatch` if the schema or hash no longer matches the projected replay row.

The handoff seal remains `MTGSim.TransitionTraceHandoffSeal.v1`, but it now includes the carried trace-entry schema/hash beside `transition_result_trace_entry_hash(result)`. That makes stale carried evidence fail before the broader trace-handoff proof, and a fully resealed malicious projection still falls through to the causal receipt/result seam.

The regression `test_transition_result_carries_first_class_trace_entry_seal` proves active schema publication, nonzero carried hash evidence, exact equality with `action_trace_entry_hash(action_trace_entry_from_transition_result(result))`, trace handoff binding, and stable diagnostics for schema/hash drift. `test_transition_trace_handoff_uses_canonical_trace_entry_hash` also asserts that page-location projection drift localizes first to the trace-entry seal unless every derived seal is maliciously recomputed, in which case receipt/result verification rejects it.

This is intentionally a small refactor: it does not change `ActionTrace.v16`, receipt serialization, or replay artifact formats. It strengthens the immediate transition result as a trustworthy boundary object for replay, fuzz, search, and agent callers.
