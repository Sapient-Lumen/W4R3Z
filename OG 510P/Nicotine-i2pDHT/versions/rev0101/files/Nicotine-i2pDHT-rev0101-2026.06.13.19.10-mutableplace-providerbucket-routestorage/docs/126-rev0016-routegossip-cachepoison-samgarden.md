# rev0016 — routegossip / cachepoison / samgarden

rev0016 continues the risk-first DHT work from three starting places that intentionally do not look alike:

1. **Route-gossip repair** — stale or failed contacts need replacement, but gossip itself is a capture vector.
2. **Repeated-round cache poisoning** — witness evidence and lookup transcripts may look fine alone but bad across repeated rounds.
3. **SAM garden shadows** — future giving nodes need inbound/outbound/reconnect transcript shapes before live I2P transport work begins.

The audit/refactor lane focuses on the provider-plane split. `provider_poison.py` remains the canonical current provider memory/quarantine surface; `providerpoison.py` remains legacy until imports are moved or adapters are written.

## New code

```text
src/i2p_dht_lab/routegossip.py
src/i2p_dht_lab/cachepoison.py
src/i2p_dht_lab/samgarden.py
src/i2p_dht_lab/provider_refactor.py   # extended
src/i2p_dht_lab/samshadow.py           # STREAM ACCEPT/CLOSED shadow support
tests/test_rev0016_routegossip_cachepoison_samgarden.py
```

## Strongest guess

```text
Route repair, cache memory, and SAM transport assumptions must be pressure-tested across repeated rounds before live I2P noise can hide design errors.
```

## What passed

The cloudtainer lane now covers 148 tests. The local evidence lane checks surface metadata, the rev0016 micro-simulation, pytest, compileall, cube audit, and zip integrity.

## Nonclaims

No live I2P/SAM transport exists. No production DHT exists. Route-gossip contacts are synthetic. Family labels are local test hints, not independence proof. Witness/cache decisions are local pressure gauges, not consensus, reputation, or truth.
