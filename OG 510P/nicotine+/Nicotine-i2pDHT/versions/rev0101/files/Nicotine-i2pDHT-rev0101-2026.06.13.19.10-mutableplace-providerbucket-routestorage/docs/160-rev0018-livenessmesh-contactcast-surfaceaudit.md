# rev0018 — livenessmesh / contactcast / surfaceaudit

rev0018 combines three parallel pressure families instead of flattening them into one story.

## 1. Liveness and resurrection pressure

`livenessbudget.py` joins adaptive lookup results with private-ish provider probe planning. It treats raw-key exposure, decoy ratio, fast-window capture, useful refusals, and metadata points as a bounded local spend.

`tombmesh.py` joins tombstone-cache reports, witness-cache summaries, and mutable-head observations so stale alive/provider evidence does not casually resurrect withdrawn, deleted, compromised, or revoked things.

`provider_compat.py` records the compatibility/refactor state of the older `providerpoison.py` surface and the current `provider_poison.py` surface.

## 2. Entrance and replica pressure

`contactlease.py` treats DHT entrances as short-lived signed leases with monotonic sequence memory, rollback detection, same-sequence fork pressure, purpose coverage, and family-diverse portfolio selection.

`siblingcast.py` plans family-capped sibling STORE/ANNOUNCE work and now also analyzes exact-digest sibling store acknowledgements. A useful refusal can prove capacity/reachability, but it does not count as a stored replica.

`sweepaudit.py` audits region-ledger reprovide plans for budget overrun, source-family monoculture, and tombstones buried behind ordinary provider work.

## 3. Map and audit pressure

`keyspacecartography.py` keeps local XOR-region observations, stale pruning, hole detection, and scout actions. It is a local routing-health tool, not a global map.

`surfaceaudit.py` and `surfaceledger.py` keep the cube honest about active public/head-registry pointers and the module/test/doc surface of new rev0018 work.

## Strongest rule

```text
A valid signature is only one typed observation. Acceptance still needs freshness, scope, family diversity, budget, and local history.
```

## Nonclaim

No live I2P/SAM transport, production DHT, private retrieval guarantee, global reputation system, mutable-head consensus, or Sybil/anonymity guarantee is implemented here.
