# Wake from amnesia — rev0015

You are in `rev0015 witnesscache-routingpressure-samshadow`.

The cube is a Python-first, consumer-agnostic DHT design lab for a mutable Kademlia-like DHT over I2P.  It is not a production network and has no live SAM transport.

## What rev0015 added

- `witnesscache.py`: local witness receipt cache with aging, dedupe, family caps, contradiction quarantine, and deterministic summaries.
- `lookuptranscript.py`: explicit lookup transcript objects and pressure analysis for path families, fast-window capture, timeouts, bad responses, and evidence-only lookups.
- `samshadow.py`: no-network SAM transcript fixtures for streaming-first integration assumptions.
- `gardenscheduler.py`: multi-window garden work scheduling and starvation pressure for protected work.
- `provider_refactor.py`: provider-plane surface audit documenting `provider_poison.py` as canonical while keeping `providerpoison.py` historical.

## Strongest current design sentence

```text
Freshness, path pressure, and transport assumptions are separate evidence surfaces; do not let one valid signature blur them together.
```

## Local lane

```text
scripts/evidence/check_surfaces.py
scripts/evidence/run_micro_simulation.py
scripts/evidence/run_cube_audit.py
PYTHONDONTWRITEBYTECODE=1 pytest -q
PYTHONDONTWRITEBYTECODE=1 python -m compileall -q src tests scripts
```

The rev0015 package lane passed with 137 tests.

## Next revision pointer

rev0016 should probably be `routegossip-cachepoison-samgarden`:

- connect lookup transcripts to witness cache summaries;
- test cache poisoning across repeated lookup rounds;
- add SAM shadow session transcript families for inbound accept, reconnect, and naming lookup failure;
- start fake route-gossip repair and stale-contact eviction;
- migrate one provider caller away from legacy `providerpoison.py` or turn it into a compatibility wrapper.
