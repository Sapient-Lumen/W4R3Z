# rev0170 — Replay paid-action journal bundle

rev0170 targets the risky artifact seam where paid-action transaction evidence could be generated and verified, but not required by the replay bundle that claims the final state.

## Problem

The replay bundle already proved a deterministic path from `StateCoreSnapshot.v1` through `ActionTrace.v16` to an expected final StateCore hash. Separately, `PaidActionTransactionJournal.v3` proved paid-action declaration/payment/rollback receipts. Those two facts were adjacent rather than bundled: an auditor could verify replay and forget to load the paid-action journal.

## Change

Newly emitted manifests use `ReplayArtifactManifest.v3`. The manifest keeps the old snapshot/trace/checkpoint/final-state fields and adds an explicit paid-action journal attachment contract:

- `paid_action_journal_attached`
- `paid_action_journal_format`
- `paid_action_journal_text_hash`
- `paid_action_journal_record_count`
- `paid_action_journal_state_hash`
- `paid_action_journal_journal_hash`
- `paid_action_journal_record_payload_hash`

`make_replay_artifact_manifest_with_paid_action_journal(...)` binds those fields. `verify_replay_artifact_bundle_with_paid_action_journal(...)` first rejects text-byte drift, then replays the action trace, then verifies the paid-action journal against the replayed final state.

## Failure policy

An attached manifest intentionally fails the old three-file verifier with `PaidActionJournalMissing`. This is the compatibility rule that keeps old detached bundles working while making new attached bundles fail closed when the paid-action journal is omitted.

The new verifier also reports typed failures for text hash, parse/semantic verification, record count, state hash, journal hash, and record-payload hash drift.

## CLI surface

rev0170 adds a four-file CLI path:

```text
mtgsim_cli --write-paid-replay-bundle-demo SNAPSHOT TRACE JOURNAL MANIFEST
mtgsim_cli --verify-paid-replay-bundle SNAPSHOT TRACE JOURNAL MANIFEST
mtgsim_cli --paid-replay-bundle-roundtrip SNAPSHOT TRACE JOURNAL MANIFEST
```

CTest coverage includes `mtgsim_cli_paid_replay_bundle_roundtrip`; `mtgsim_cli_replay_bundle_roundtrip` remains the detached `ReplayArtifactManifest.v3` compatibility smoke path.

## Audit result

This is an artifact trust refactor rather than a broad rules expansion. It reduces omission risk: paid-action cost/payment receipts are now either explicitly absent (`paid_action_journal_attached=0`) or required and hash-bound (`paid_action_journal_attached=1`). The next high-risk seam is making the cost-plan transaction kernel reusable for nonmana costs instead of continuing to grow paid-action receipts one witness at a time.
