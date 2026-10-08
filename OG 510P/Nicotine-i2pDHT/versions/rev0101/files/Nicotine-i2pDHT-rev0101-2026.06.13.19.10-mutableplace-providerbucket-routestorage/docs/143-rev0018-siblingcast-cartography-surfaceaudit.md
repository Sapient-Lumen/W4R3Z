# rev0018 — `siblingcast-keyspacecartography-surfaceaudit`

rev0018 keeps the cube DHT-first and implements two different risky edges before live transport:

1. **Sibling broadcast replication pressure.** Closest-node storage is not enough. The lab now requires signed storage receipts, family diversity, close-window coverage, contradiction detection, and useful-refusal handling before a replicated record is locally considered healthy.
2. **Keyspace cartography.** A node can have many contacts and still see only a captured slice of keyspace. The lab now maps small XOR-prefix regions, detects holes, stale observations, family monoculture, and introducer monoculture, then emits bounded scout work.
3. **Surface-pointer audit/refactor.** The cube now has a gentle audit layer for JSON path pointers and revision drift, separate from the fail-closed public surface checker.

The strongest sentence for this revision:

```text
Replication health and routing coverage are different local truths; neither should be inferred from a fast, signed, or close-looking answer alone.
```

## New Python surface

```text
src/i2p_dht_lab/siblingbroadcast.py
src/i2p_dht_lab/keyspacecartography.py
src/i2p_dht_lab/surfaceaudit.py
tests/test_rev0018_sibling_cartography_surfaceaudit.py
```

## Audit/refactor lane

`cubeaudit.py` now treats the VERSION/pyproject/README version check as a full-cube check, not something that breaks small temporary audit fixtures. `surfaceaudit.py` adds a broader, non-failing JSON pointer audit for wake-from-amnesia hygiene.

## Nonclaims

No live I2P/SAM transport, production DHT, production STORE protocol, global keyspace map, global reputation, Sybil solution, private retrieval, or application integration is implemented.
