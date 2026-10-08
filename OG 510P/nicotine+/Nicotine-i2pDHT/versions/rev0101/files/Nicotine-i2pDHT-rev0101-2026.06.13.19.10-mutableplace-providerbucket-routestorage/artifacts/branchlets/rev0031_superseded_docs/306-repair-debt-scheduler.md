# Repair debt scheduler

`repairdebt.py` models local repair triggers as typed debt instead of immediate side effects.

Debt kinds include tombstones, revocations, mutable heads, provider proofs, peer deltas, route gossip, custody, and negative-space repair. Severity separates hard-negative, control-plane, entrance, and bulk work.

The scheduler tests:

- expired debt
- replayed debt
- same-sequence conflicting evidence
- source-family monoculture
- low family diversity for control-plane repairs
- tombstone/revocation-first scheduling
- byte and item budget deferral

The point is not to decide truth. The point is to keep repair pressure typed and budgeted before clients or garden nodes spend bandwidth and attention.
