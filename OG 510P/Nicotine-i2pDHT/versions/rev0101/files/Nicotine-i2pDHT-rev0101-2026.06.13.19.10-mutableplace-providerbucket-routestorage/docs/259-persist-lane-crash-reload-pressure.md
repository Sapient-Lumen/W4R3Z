# Persist lane crash/reload pressure

`src/i2p_dht_lab/persistlane.py` models signed canonical snapshots for local evidence lanes. The goal is not to invent the final database format. The goal is to test the dangerous restart edge early.

Risk guesses pinned in tests:

- persisted bytes must pass parseguard before structure is trusted;
- snapshots are signed;
- snapshots carry monotonic sequence and previous-snapshot digest;
- lower-sequence reloads are rollback pressure;
- same-sequence different snapshots are fork pressure;
- higher-sequence snapshots that do not link to local memory are previous-link pressure;
- compaction must preserve hard negatives such as tombstones, revocations, and provider-false records.

This matters because a future I2P DHT will depend on local memory for highest-seen mutable heads, revocation heads, witness evidence, tombstones, route leases, and provider claims. Dropping hard negative evidence after restart can resurrect stale state.
