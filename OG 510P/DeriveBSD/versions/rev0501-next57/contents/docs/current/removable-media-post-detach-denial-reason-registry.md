# Current removable-media post-detach denial reason registry

The current post-detach denial selector is `removable.media.local.post_detach.denial.reason.registry`.

The registry exists because r521-r523 made post-detach receipts executable, but cause selection still needed a single precedence surface. Brokers should not infer the winning denial reason from prose, scenario names, or whichever check failed first.

## Current precedence rule

The rule is `lower-rank-wins`.

The current ranked codes are:

| Rank | Code | Meaning |
| ---: | --- | --- |
| 5 | `raw-support-visibility` | A support/debug path exposed raw state; fail closed before releasing a projection. |
| 10 | `tombstone-visible` | Legacy r510 stale-authority denial after tombstone. |
| 20 | `expired-ledger-root-fresh-authority-required` | Expired compacted reader-use ledger root cannot be observed and requires fresh authority. |
| 30 | `stale-root` | Rollback, fork, or stale attempted root. |
| 40 | `missing-expiry-receipt` | Missing expiry proof fails closed. |
| 50 | `degraded-clock` | Degraded, skewed, or unavailable time proof fails closed. |
| 70 | `missing-fresh-authority` | Subordinate context; does not preempt the primary reason. |
| 80 | `rate-limit-replayed-no-new-debit` | Idempotent replay behavior; reuses prior denial without another debit. |
| 900 | `none-successor-authority` | Non-denial success after fresh authority is consumed and a successor root is admitted. |

Every reason carries `support-safe-digest-only`. The registry checker rejects any reason that attempts to make raw support/debug visibility acceptable.

## Joins checked by the guardrail

`tools/check_removable_media_local_post_detach_denial_reason_registry.py` recomputes and checks bindings to:

- the r521 state-machine manifest;
- the r522 scenario replay manifest;
- the r523 transition witness capsule;
- the r521 post-expiry enforcement ledger receipt;
- the r521 fresh-authority recovery receipt;
- the legacy r510 denial receipt.

It also proves that scenario reason codes match the replay manifest, witness trace IDs match the transition witness capsule, the enforcement ledger's `denial_precedence_rank` matches the registry, and successor recovery does not resurrect the expired root.

## Implementation floor

A broker may attach subordinate reasons for support triage, but subordinate codes must not outrank the primary cause. In particular, `missing-fresh-authority` is context under `expired-ledger-root-fresh-authority-required`; it is not a separate successful recovery path.

The r525 selection receipt `removable.media.local.post_detach.denial.selection.receipt` is the per-attempt proof that this registry was applied correctly.

Last updated: 2026-05-30r525
