# Wake from amnesia — rev0018 combined

The cube is `rev0018 livenessmesh-contactcast-surfaceaudit`.

## What happened

rev0018 has more than one origin thread:

- liveness/metadata budgets between adaptive lookup and provider probes;
- tombstone mesh pressure across tombstones, witnesses, and mutable heads;
- provider compatibility/refactor mapping;
- sibling-broadcast/store receipt pressure;
- keyspace cartography and scout planning;
- contact leases for fresh entrance memory;
- region sweep audits and active surface-ledger refactor.

## Why it matters

The DHT is not only a lookup algorithm. It is a collection of local judgment surfaces under anonymity, churn, replay, and generous garden nodes. The hard parts are not just cryptographic validation; they are deciding when a locally valid observation should or should not change behavior.

## Start points

```text
src/i2p_dht_lab/livenessbudget.py
src/i2p_dht_lab/tombmesh.py
src/i2p_dht_lab/provider_compat.py
src/i2p_dht_lab/contactlease.py
src/i2p_dht_lab/siblingcast.py
src/i2p_dht_lab/siblingbroadcast.py
src/i2p_dht_lab/keyspacecartography.py
src/i2p_dht_lab/sweepaudit.py
src/i2p_dht_lab/surfaceaudit.py
src/i2p_dht_lab/surfaceledger.py
```

## Next likely work

Join contact leases to route-gossip eviction, feed sibling store receipts into mutable-head/tombstone repair, produce signed garden budget receipts when sweep audit throttles work, and continue reducing historical surface ambiguity with explicit ledgers rather than deletion.

## Verification expectation

```text
surface check
micro-simulation
pytest: 188 passed
compileall
cube audit
zip integrity check
```
