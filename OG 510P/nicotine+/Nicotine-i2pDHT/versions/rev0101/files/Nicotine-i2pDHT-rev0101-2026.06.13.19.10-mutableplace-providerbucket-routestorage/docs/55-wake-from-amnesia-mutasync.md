# Wake-from-amnesia notes — mutasync

Remember this first:

> Mutable heads are the DHT feature.  Sync is one future consumer.

rev0006 did not implement sync.  It planted the DHT-side primitives sync will need.

## Current mental model

```text
DHT over I2P
  -> signed mutable slots
      -> mutable torrent heads
      -> feed tips
      -> roster heads
      -> snapshot heads
      -> garden catalogs
  -> provider records
      -> encrypted blocks
      -> feed segments
      -> manifests
      -> garden services
```

## Why per-writer feeds?

Multiwriter folders are awkward with one mutable slot.  Per-writer feeds let devices work offline, preserve authorship, avoid shared write keys, and make rollback/fork observations visible.

## Why gardens?

Garden nodes keep the sync graph alive while leaves sleep.  They watch heads, cache encrypted blocks, mirror manifests, hold tombstones, relay feeds, and publish graceful refusals.  They cannot author changes.

## Where to look

1. `docs/48-rev0006-mutasync-gardenlog-dream.md`
2. `docs/49-mutasync-record-algebra.md`
3. `docs/50-garden-nodes-for-mutasync.md`
4. `docs/51-sync-conflict-capability-threat-guesses.md`
5. `src/i2p_dht_lab/mutasync.py`
6. `tests/test_mutasync.py`

## Next useful cube

`rev0007 chaossync-faketransport-headwatch`: fake async transport and adversarial simulation for stale heads, false providers, garden overload, roster rollback, feed forks, and sync catch-up under I2P-like latency.
