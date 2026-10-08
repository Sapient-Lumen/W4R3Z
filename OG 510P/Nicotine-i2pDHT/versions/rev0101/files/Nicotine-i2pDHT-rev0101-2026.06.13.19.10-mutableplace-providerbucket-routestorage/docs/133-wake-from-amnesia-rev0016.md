# Wake from amnesia — rev0016

Current revision:

```text
rev0016 routegossip-cachepoison-samgarden
```

The cube is still a Python-first DHT design lab over I2P. It is not a production DHT and has no live I2P transport.

## New mental model

```text
route repair is useful but capturable
witness cache is useful but replayable
SAM transport should be shadowed before it is real
provider refactors should leave receipts before deleting history
```

## New files

```text
src/i2p_dht_lab/routegossip.py
src/i2p_dht_lab/cachepoison.py
src/i2p_dht_lab/samgarden.py
tests/test_rev0016_routegossip_cachepoison_samgarden.py
```

## Important old files still active

```text
src/i2p_dht_lab/witnesscache.py
src/i2p_dht_lab/lookuptranscript.py
src/i2p_dht_lab/samshadow.py
src/i2p_dht_lab/provider_refactor.py
src/i2p_dht_lab/provider_poison.py
src/i2p_dht_lab/providerpoison.py  # legacy, still imported by historical tests
```

## What the tests now pin

```text
route gossip can evict stale contacts and accept diverse repair
route gossip quarantines one-introducer capture
cache poison detects transcript replay monoculture
cache poison detects repeated captured-fast windows
cache poison preserves contradiction quarantine
SAM garden shadows validate inbound accept/reconnect/naming families
SAM garden shadows reject ephemeral destination profiles
provider migration plan sees remaining legacy callers
```

## Verification

```bash
scripts/ci/run_python_cloudtainer_lane.sh
```

Expected rev0016 result:

```text
surface check
micro-simulation
pytest: 148 passed
compileall
cube audit: pass with info-only historical findings
```

## Next pointer

```text
rev0017 regionledger-adaptivealpha-witnessrepair
```

Suggested focus: adaptive alpha/beta lookup policy, route-gossip contact succession, region-sweep provider ledgers for garden scheduling, cache-poison/tombstone interactions, and continuing the provider-surface migration.
