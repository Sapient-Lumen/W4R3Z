# Current removable-media post-detach rate-limit debit ledger

The current debit ledger receipt is `removable.media.local.post_detach.rate_limit.debit.ledger.receipt`.

It exists because a denial-selection receipt can say `rate_limit_action = debit`, but that does not by itself prove the rate-limit ledger advanced exactly once or that idempotent replay avoided a double debit.

## Current rule

For the first expired-root denial:

- selected reason: `expired-ledger-root-fresh-authority-required`;
- selected rate-limit action: `debit`;
- debit amount: one redacted post-expiry denial attempt unit;
- CAS expected root: the prior rate-limit root;
- CAS result: committed with a new rate-limit root;
- retry posture: `bounded-redacted-retry-window`;
- support visibility: `support-safe-digest-only`.

For an idempotent replay with the same key:

- the same denial is returned;
- the replay is not treated as a new authority attempt;
- the replay debit amount is zero;
- double debit remains forbidden.

## Support projection

Support/debug consumers may see the selected reason, retry class, fresh-authority instruction, and digest-level evidence. They must not see raw budget counts, ledger roots, raw subjects, or raw idempotency keys.

## Guardrail

Run:

```text
python3 tools/check_removable_media_local_post_detach_rate_limit_debit_ledger_receipt.py
```

The checker recomputes source digests for the r521 enforcement ledger, r525 denial selection, r524 reason registry, r522 scenario replay, r523 transition witness, and r521 support projection. It also rejects CAS mismatch, double debit on idempotent replay, non-advancing roots, missing debit, policy drift, stale selection bindings, support-visible budget data, and unbounded retry windows.

Last updated: 2026-05-30r526
