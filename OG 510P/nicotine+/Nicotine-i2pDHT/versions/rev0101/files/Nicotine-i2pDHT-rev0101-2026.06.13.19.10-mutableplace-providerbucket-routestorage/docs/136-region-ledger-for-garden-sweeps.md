# Region ledger for garden sweeps

Region sweep is the garden-node answer to provider reannounce storms. A high-volume garden should not do one expensive lookup per key. It should batch by XOR keyspace region, smooth work over time, and preserve refusal/tombstone memory.

`regionledger.py` adds a local ledger in front of `sweep.py`.

The ledger remembers:

```text
advertisement key/kind/namespace
source family
first seen / last seen / last published
live tombstones
region prefix
batch weight
```

The current behavior:

- live tombstones suppress matching advertisements so dead things are not reannounced;
- tombstone-only batches can be scheduled to keep withdrawal evidence alive;
- large same-source-family floods are quarantined before becoming garden sweep work;
- due work is grouped by region and split by weight;
- published batches can be marked so repeated planning changes deterministically.

This is not provider truth. A region ledger only decides whether this garden should spend capacity on a record now.
