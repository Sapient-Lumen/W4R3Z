# rev0018 — contactlease / siblingcast / sweepaudit

This revision goes risk-first in two deliberately different places:

1. **Entrance/contact leases**: how a node should keep, renew, reject, and select signed contact-card entrances without letting stale cards or captured introducer families become the new center.
2. **Sibling broadcast / replica pressure**: how a node should treat a DHT store round as incomplete until enough family-diverse siblings acknowledge the exact record digest.

It also adds a garden **sweep audit** and a small **surface ledger** refactor so new active modules are named with their tests and docs.

The strongest new guess:

```text
Entrance growth and replica durability are both capture surfaces; freshness and family diversity must be checked before convenience wins.
```

## New modules

```text
src/i2p_dht_lab/contactlease.py
src/i2p_dht_lab/siblingcast.py
src/i2p_dht_lab/sweepaudit.py
src/i2p_dht_lab/surfaceledger.py
```

## New tests

```text
tests/test_rev0018_contactlease_siblingcast_sweepaudit.py
```

## Nonclaims

No live I2P/SAM transport is implemented. No production DHT is implemented. Contact-family labels are deterministic local hints, not a proven Sybil oracle. Sibling acknowledgements and sweep audits are local pressure objects, not consensus.
