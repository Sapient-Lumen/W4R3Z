# rev0017 — `regionledger-adaptivealpha-witnessrepair`

rev0017 keeps the cube in DHT-only design space and continues the risk-first rule: implement the parts most likely to lie to us before polishing live transport.

## New hard surfaces

1. **Adaptive alpha/beta lookup pressure**: `adaptivealpha.py` looks at recent lookup transcripts and decides whether to accept, widen disjoint concurrency, increase timeout patience, hold under useful refusals, or quarantine a captured fast window.
2. **Region ledger**: `regionledger.py` puts a garden-facing memory layer in front of region sweeps so provider/mutable/contact advertisements are scheduled by keyspace region, source family, tombstone suppression, and batch weight rather than FIFO.
3. **Tombstone/cache resurrection pressure**: `tombstonecache.py` models signed deletion/withdrawal/revocation evidence and tests whether stale witness/provider evidence tries to resurrect dead things.
4. **Witness repair planning**: `witnessrepair.py` converts aged, low-diversity, or contradictory witness-cache summaries into bounded next actions.
5. **Provider audit/refactor**: `provider_refactor.py` now distinguishes historical legacy imports from active legacy imports, making the eventual `providerpoison.py` wrapper migration less ambiguous.

## Strong sentence

```text
Do not let latency, stale cache evidence, or regional reprovide pressure silently choose truth for the DHT.
```

## Nonclaims

No live I2P/SAM transport is implemented. No production DHT is implemented. The adaptive alpha policy is a deterministic local toy policy, not a measured I2P optimizer. Tombstones are signed local evidence objects, not a global deletion consensus. Region ledgers are garden scheduling memory, not provider truth. Witness repair plans are bounded local next actions, not a witness quorum.
