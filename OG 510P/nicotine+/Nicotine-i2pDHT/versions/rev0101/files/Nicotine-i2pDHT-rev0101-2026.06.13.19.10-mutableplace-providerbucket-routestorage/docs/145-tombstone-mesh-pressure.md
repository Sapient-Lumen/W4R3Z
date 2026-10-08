# Tombstone mesh pressure

Tombstones are evidence for withdrawals, mutable deletion, key compromise, and grant revocation. They are not global deletion truth. But ignoring them makes stale provider and witness caches dangerous.

`TombstoneCache` already detects live tombstones, tombstone forks, and resurrection pressure. rev0018 adds `tombmesh.py`, which combines:

```text
live tombstone records
issuer families
cached witness-summary alive/latest/provider weights
mutable head events
highest tombstone sequence
highest observed head sequence
```

The first mesh decisions are:

```text
no_tombstone_pressure
preserve_tombstone
block_resurrection_mesh
ask_more_independent_witnesses
quarantine_tombstone_fork
quarantine_head_after_compromise
```

The key new pressure test is key-compromise interaction: a newer/equal mutable head after a live key-compromise tombstone should not be accepted merely because it is signed. That is not consensus; it is local evidence hygiene.
