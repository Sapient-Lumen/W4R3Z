# rev0019 — lease-bound route gossip pressure

Route gossip was previously tested as a stale-contact repair mechanism. Contact leases were previously tested as fresh, signed entrance evidence. rev0019 joins them because the dangerous failure is the seam: a batch can be close and diverse while carrying contacts whose signed lease expired, forked, or never allowed route use.

The new rule is: **route repair commits only when selected contacts are backed by fresh, monotonic, purpose-scoped route leases.** A lease is still not global truth. It is local anti-staleness evidence that blocks immortal bootstrap folklore and replayed entrances.

`leaseroute.py` adds `LeaseRouteBook`, `LeaseRoutePolicy`, and `assess_leased_route_gossip()`. It evaluates route-gossip batches in a copy of local route memory, checks the selected contacts against live `ContactLeasePurpose.ROUTE` leases, and commits the repair only after both route-gossip diversity and lease coverage pass.

Test pressure:

- diverse leased gossip commits to route memory;
- selected unleased contacts quarantine the repair;
- stale local contacts can be evicted only when replacement contacts are lease-backed;
- same-sequence lease fork pressure blocks route repair.
