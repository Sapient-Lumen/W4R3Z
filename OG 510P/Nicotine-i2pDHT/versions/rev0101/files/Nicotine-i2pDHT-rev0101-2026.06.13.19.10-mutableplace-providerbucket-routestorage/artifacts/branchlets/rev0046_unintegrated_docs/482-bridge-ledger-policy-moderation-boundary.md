# Bridge ledger policy/moderation boundary

`bridgeledger.py` sits after rev0045 `shadowfire` and rev0029-style egress budgeting. It asks whether a future public bridge refresh, withdraw, or repair can be recorded as locally safe after shadow-fire, egress, moderation, and optional redress are joined.

The ledger entry is signed, scoped, sequence-numbered, previous-linked, and bound to exact component report digests.

It catches:

- missing ledger entries
- bad signatures
- replay
- rollback
- same-sequence forks
- previous-link mismatch
- profile/service/action drift
- shadow-fire action drift
- component digest drift
- egress rejection/quarantine
- active moderation blocks without lifting redress
- watch pressure that has not been explicitly allowed

The ledger still performs no live network operation. It makes the future side effect visible and testable first.
