# Python surface — rev0017

New modules:

```text
src/i2p_dht_lab/adaptivealpha.py
src/i2p_dht_lab/regionledger.py
src/i2p_dht_lab/tombstonecache.py
src/i2p_dht_lab/witnessrepair.py
```

Extended module:

```text
src/i2p_dht_lab/provider_refactor.py
```

New tests:

```text
tests/test_rev0017_regionledger_adaptivealpha_witnessrepair.py
```

Primary objects:

```text
AdaptiveAlphaPolicy
AdaptiveRoundStats
AdaptiveLookupKnobs
AdaptiveLookupReport
RegionLedger
RegionLedgerPolicy
RegionTombstone
RegionLedgerBatch
TombstoneRecord
TombstoneCache
TombstoneCachePolicy
WitnessRepairPolicy
WitnessRepairPlan
```

The tests cover:

```text
fast-window capture widens alpha/beta and blocks acceptance
timeout pressure increases alpha and timeout patience
useful refusals hold rather than flood overloaded peers
diverse lookup success accepts only without pressure
live tombstones suppress region-ledger advertisements
large source-family monoculture quarantines sweep work
region batches respect weight caps and publication memory
tombstones block cached provider resurrection pressure
tombstone forks quarantine same-issuer same-sequence conflicts
key-compromise tombstones can demand family diversity
witness repair asks missing families
witness repair quarantines contradictions
provider migration distinguishes historical legacy imports
```
