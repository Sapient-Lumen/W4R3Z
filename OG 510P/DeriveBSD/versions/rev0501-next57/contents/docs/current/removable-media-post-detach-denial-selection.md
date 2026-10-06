# Current removable-media post-detach denial selection

The current per-attempt selector is `removable.media.local.post_detach.denial.selection.receipt`.

The receipt exists because a registry alone does not prove a broker used the registry. r525 requires the broker to record observed predicates, candidate reasons, the selected reason, subordinate reason codes, support visibility, and rate-limit behavior for the concrete attempt.

## Current selection rule

The rule is `lower-rank-wins` over active non-subordinate candidates from `removable.media.local.post_detach.denial.reason.registry`.

For the current expired-root attempt:

| Candidate | Active | Rank | Role |
| --- | --- | ---: | --- |
| `raw-support-visibility` | no | 5 | sanitization failure |
| `tombstone-visible` | no | 10 | primary denial |
| `expired-ledger-root-fresh-authority-required` | yes | 20 | selected primary denial |
| `stale-root` | yes | 30 | attached context |
| `missing-expiry-receipt` | no | 40 | primary denial |
| `degraded-clock` | no | 50 | primary denial |
| `missing-fresh-authority` | yes | 70 | subordinate context |
| `rate-limit-replayed-no-new-debit` | no | 80 | idempotent replay behavior |

The selected reason is `expired-ledger-root-fresh-authority-required`. It denies observe/export/rehydrate, requires fresh authority, carries subordinate context, and keeps support visibility at `support-safe-digest-only`.

## Guardrail

Run:

```text
python3 tools/check_removable_media_local_post_detach_denial_selection_receipt.py
```

The checker recomputes source digests for the r524 denial registry, r522 scenario replay manifest, r523 transition witness capsule, r521 enforcement ledger receipt, and r521 support projection. It also rejects stale registry bindings, omitted higher-precedence reasons, unknown selected reasons, subordinate selected reasons, raw support visibility, rate-limit drift, and witness/scenario drift.

Last updated: 2026-05-30r525
