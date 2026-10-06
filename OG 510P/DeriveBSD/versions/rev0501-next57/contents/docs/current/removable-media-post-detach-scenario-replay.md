# Current removable-media post-detach scenario replay

This is the r522 current-view surface for `removable.media.local.post_detach.scenario.replay.manifest`.

## Scenarios

| scenario | expected terminal behavior | critical invariant |
|---|---|---|
| `expired-root-denied-with-enforcement-ledger` | `expired-root-denied` | expired roots cannot observe, export, or rehydrate after expiry |
| `missing-expiry-receipt-fails-closed` | `fail-closed-typed-denial` | missing expiry proof never becomes permission |
| `rollback-or-stale-root-is-rejected` | `fail-closed-typed-denial` | stale, rollback, and forked roots cannot race the ledger |
| `degraded-time-proof-fails-closed` | `fail-closed-typed-denial` | degraded time is not warning-only |
| `fresh-authority-recovers-to-successor-root-only` | `successor-root-admitted` | fresh authority admits only a successor root |
| `same-idempotency-key-replays-same-denial-without-double-debit` | `idempotent-denial-replayed` | replays do not create a second rate-limit debit |

## Executable surface

- Schema: `spec/removable.media.local.post_detach.scenario.replay.manifest.schema.json`
- Example: `spec/examples/removable.media.local.post_detach.scenario.replay.manifest.json`
- Red corpus: `spec/examples/invalid/removable-media/post-detach-scenario-replay-manifest/`
- Checker: `tools/check_removable_media_local_post_detach_scenario_replay.py`

## Model bindings

The replay manifest binds to computed canonical example digests for the r521 state-machine manifest, post-expiry enforcement ledger, fresh-authority recovery receipt, support projection, and backend evidence. The digest rule is centralized in `tools/cube_digest_lib.py`.

Last updated: 2026-05-30r522
