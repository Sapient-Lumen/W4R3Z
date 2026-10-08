# Tombstone repair after settlement

A settled effect must not erase hard-negative memory such as tombstones, revocations, and resurrection-block evidence.

`tombstonerepair.py` adds signed local observations for tombstone carried, revocation carried, repair published, resurrection blocked, and no-live-tombstone cases. Missing repair becomes watch pressure; resurrection pressure quarantines.

Tombstone repair is not global deletion truth. It is local repair evidence so stale positive records cannot casually resurrect things a node knows are withdrawn or compromised.
