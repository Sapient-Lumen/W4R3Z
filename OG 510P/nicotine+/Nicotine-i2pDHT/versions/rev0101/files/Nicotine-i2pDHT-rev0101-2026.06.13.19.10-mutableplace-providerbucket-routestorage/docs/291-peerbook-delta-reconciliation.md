# Peerbook and peer delta reconciliation

`peerbook.py` builds local entrance views from signed contact leases plus the channel that delivered them. The point is to maximize entrances without letting a single room, garden, bridge, seed list, or buddy channel become the new center.

The view requires:

- fresh valid signed contact leases
- peer-family diversity
- channel-family diversity
- enough independent channel IDs
- required purpose coverage such as route and seed-gate
- contact-lease fork rejection

`peerdelta.py` adds an exact toy delta-sketch fixture for peer-book ranges. It is not production minisketch. It pins the boundary: reconcile by compact signed summaries, detect stale/forked summaries, ask for exact deltas when small, and fall back to range resync when the difference is too large.

The peer-delta sketch records item digests, a count, an XOR digest, range id, sequence, expiry, signer key, and signature. That makes rollback, same-sequence fork, and family-monoculture pressure executable before a real set-reconciliation implementation is chosen.
