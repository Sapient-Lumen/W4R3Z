# rev0070 action trace replay check

rev0070 turns the rev0069 action receipt from a post-hoc audit row into an executable replay check. It still does not claim full checkpoint serialization, hidden-information observations, or durable file-format replay. The concrete improvement is narrower and riskier: a checkpointed `GameState` plus an exported action trace can now be replayed until the first divergent transition.

## New replay surface

`ActionTraceEntry` is a label-independent projection of `ActionReceiptRecord`:

- canonical `LegalAction` fields reconstructed by `action_from_receipt(...)`, without using `LegalAction::label`;
- `expected_action_hash`, sampled from `legal_action_hash(...)`;
- `expected_state_hash_before` and `expected_state_hash_after`, sampled from `canonical_state_hash(...)`;
- `expected_applied`, so full audit traces can include rejected illegal attempts while default replay traces omit them.

`export_action_trace(game)` returns only applied receipts by default. `export_action_trace(game, false)` includes rejected attempts for forensic audits. `replay_action_trace(game, trace)` applies entries against the caller-provided checkpoint and reports an `ActionReplayResult` that stops at the first divergent transition.

## Failure modes caught early

The replay checker detects:

- action-hash mismatches before mutating the checkpoint;
- pre-state hash mismatches before applying an action;
- applied/rejected result mismatches;
- post-state hash mismatches immediately after the action.

This is intentionally step-local. A long fuzz or agent run should no longer need to finish before discovering that an earlier transition diverged.

## Audit/refactor

Validation now uses `action_from_receipt(...)` instead of duplicating the receipt-to-action projection. This removes a drift hazard where replay export and receipt validation could canonicalize the same row differently.

The datacube audit now has an `action_trace_wiring` probe covering the new public API, tests, docs, and ledger notes.

## Remaining gap

This is not yet serialized replay. The next high-value step remains a canonical checkpoint/state snapshot format and a cross-process test that `checkpoint + ActionTraceEntry[]` reconstructs the same final `StateCore` hash from disk.
