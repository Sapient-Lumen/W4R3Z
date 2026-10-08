# Tombstone repair after settlement

`tombstonerepair.py` blocks a subtle failure: a settled effect can make the system feel clean while stale positive evidence resurrects something that had a live tombstone, revocation, withdrawal, or compromise notice.

Repair entries are signed observations for:

```text
tombstone_carried
revocation_carried
repair_published
resurrection_blocked
soft_none
```

The lane accepts no-live-tombstone cases quickly, but if live tombstones are expected, it requires carried repair evidence with family/path diversity. Any resurrection pressure quarantines the repair decision instead of treating repair as complete.

This is not global deletion truth. It is local hard-negative preservation at the exact settlement boundary.
