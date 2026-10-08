# Python surface — rev0016

New modules:

```text
src/i2p_dht_lab/routegossip.py
src/i2p_dht_lab/cachepoison.py
src/i2p_dht_lab/samgarden.py
```

Extended modules:

```text
src/i2p_dht_lab/samshadow.py
src/i2p_dht_lab/provider_refactor.py
```

New tests:

```text
tests/test_rev0016_routegossip_cachepoison_samgarden.py
```

## Route gossip

```text
RouteContact
RouteGossipBatch
RouteGossipPolicy
RouteGossipBook.ingest_gossip()
```

Tests cover stale eviction, low diversity, and introducer capture.

## Cache poison

```text
CacheRound
CachePoisonPolicy
analyze_cache_poison_rounds()
```

Tests cover stable diverse rounds, transcript replay, fast-window reinforcement, and contradictions.

## SAM garden

```text
SamGardenProfile
make_sam_garden_cases()
analyze_sam_garden_cases()
```

Tests cover inbound accept, reconnect/naming families, datagram-primary negative assumptions, and ephemeral destination rejection.

## Provider refactor

```text
find_provider_legacy_imports()
plan_provider_surface_migration()
```

Tests pin the fact that one historical legacy import remains and must be migrated or adapted before wrapper conversion.
