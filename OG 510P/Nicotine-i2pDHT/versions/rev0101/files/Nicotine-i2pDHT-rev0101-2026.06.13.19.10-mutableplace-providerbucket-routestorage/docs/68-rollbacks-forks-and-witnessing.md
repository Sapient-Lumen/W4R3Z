
# Rollbacks, forks, and witnessing

Mutable DHT records are signed, but signatures do not solve time.

## Stale-but-valid is the normal attack

A record at sequence 5 may be valid, but if a client already saw sequence 12, sequence 5 is suspicious. The client needs local monotonic memory.

## Same-sequence fork

If a publisher signs two different values at the same sequence, both can verify. Local slot stores should reject equal-sequence different-value updates, but distributed lookups may still discover split views.

The cube's `analyze_head_observations()` intentionally treats this as evidence:

```text
same seq + different value digests => fork alert
observed seq < known seq          => stale/rollback alert
observed seq > known seq          => advanced head
```

## Garden witness role

Gardens should preserve:

- highest-seen sequence receipts;
- same-sequence fork evidence;
- stale-head observations;
- policy/seed head history;
- tombstone and revocation heads.

A garden witness does not decide truth. It helps clients avoid amnesia.

## Transparency influence

The design borrows the witness idea from transparency systems: useful monitors and witnesses can detect split views or rollback, but they should not become mandatory global authorities.
