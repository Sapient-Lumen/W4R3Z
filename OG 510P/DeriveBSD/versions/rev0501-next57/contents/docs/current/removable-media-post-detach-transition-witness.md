# Current removable-media post-detach transition witness

`transition-witness-capsule-positive-and-negative-fixture-guarded` is the r523 floor for reviewing post-detach scenario behavior below the outcome level.

The canonical witness artifact is `removable.media.local.post_detach.transition.witness.capsule`. It binds to the computed digests of the r521 state-machine manifest, the r522 scenario replay manifest, the enforcement-ledger receipt, the fresh-authority recovery receipt, the support projection, and the FreeBSD backend evidence.

## Trace requirements

Every r522 scenario has exactly one trace. Each trace records:

- ordered, contiguous step indexes;
- known from/to state names;
- required dotted receipt kinds;
- computed receipt digests;
- allowed observe/export/rehydrate actions after each step;
- rate-limit behavior;
- idempotency behavior;
- time posture;
- support visibility;
- a computed outcome digest.

## Current terminal states

- `expired-root-denied` is the terminal state for ordinary post-expiry attempts.
- `fail-closed-typed-denial` is the terminal state for missing expiry proof, stale/rollback roots, and degraded time.
- `successor-root-admitted` is the only positive fresh-authority recovery state.
- `idempotent-denial-replayed` is the terminal state for a repeated post-expiry attempt using the same idempotency key.

## Non-negotiable invariants

- Expired roots are never observable after expiry.
- Fresh-authority recovery never resurrects the expired root; it admits only a successor root.
- Idempotent denial replay does not double-debit the rate-limit ledger.
- Support/debug visibility remains `support-safe-digest-only`.
- Witness outcome digests are computed from trace content rather than symbolic placeholders.

Run:

```text
python3 tools/check_removable_media_local_post_detach_transition_witness.py
```

Last updated: 2026-05-30r523
