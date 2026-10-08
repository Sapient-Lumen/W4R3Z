# rev0056 — recoverymesh-safecleanup-chaosbudget

rev0056 moves one step past `effectseal`: an effect that survived restart chaos and fuzz-shrink pressure is still not safe to treat as clean, compacted, or endlessly rehearseable.

The new risk-first seam is:

```text
effect seal accepted
+ restart chaos accepted
+ fuzz shrink accepted
    ≠ recovery state is clean
    ≠ cleanup may delete evidence
    ≠ repeated chaos/fuzz work may spend unbounded budget
```

New active surfaces:

- `sealreplay.py` — signed observations across restart generations so committed/aborted effects cannot be quietly reinterpreted.
- `corpuswitness.py` — signed witness receipts for fuzz-shrink/corpus decisions.
- `recoverymesh.py` — joined reducer across effect seal, seal replay, restart chaos, and corpus witnesses.
- `safecleanup.py` — signed cleanup tickets that preserve accepted seals and hard negatives.
- `chaosbudget.py` — signed post-effect budget grants for restart replay, cleanup, fuzz shrink, retry probes, dead letters, and SAM canaries.
- `recoveryfold.py` — rev0056 audit/refactor fold preserving rev0055 `restartfold` predecessor history.

Strong sentence:

```text
An accepted effect is not clean merely because it survived restart; recovery, cleanup, and further chaos work each need exact-boundary evidence.
```

## Nonclaims

No live I2P/SAM transport. No production DHT. No production recovery database, cleanup engine, or budget scheduler. No global reputation. No mutable-head consensus. No private retrieval guarantee. No Sybil/anonymity guarantee. No Nicotine+ patch.
