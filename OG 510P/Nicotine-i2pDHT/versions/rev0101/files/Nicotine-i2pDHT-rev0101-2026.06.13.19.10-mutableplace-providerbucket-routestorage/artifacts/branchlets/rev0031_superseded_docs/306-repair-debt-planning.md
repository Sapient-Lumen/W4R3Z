# Repair-debt hard-negative scheduling

Garden nodes can give bandwidth, RAM, storage, and attention. Without a repair-debt lane, that generosity can be captured by bulk soft work while tombstones, revocations, provider-false receipts, and key-crisis repairs wait behind convenience.

`repairdebt.py` models repair pressure as signed typed debt:

```text
tombstone / revocation / key_crisis / provider_false -> hard-negative debt
mutable_head / custody / peer_delta / route / provider_true -> repair debt
```

The planner verifies signatures and freshness, checks sequence rollback and same-sequence forks, applies source/path family pressure, reserves budget for hard negatives, then chooses bounded work. Soft repairs may be useful, but they cannot launder themselves ahead of cheap hard-negative work.

This is not a market, not a global reputation system, and not payment. It is local capacity selection under pressure.
