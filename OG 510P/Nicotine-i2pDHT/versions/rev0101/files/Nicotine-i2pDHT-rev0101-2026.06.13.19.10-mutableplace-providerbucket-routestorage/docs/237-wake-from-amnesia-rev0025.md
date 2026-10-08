# Wake from amnesia — rev0025

Start here:

1. `docs/231-rev0025-capgate-evidencegc-splitmerge.md`
2. `docs/232-capability-dispatch-gate.md`
3. `docs/233-evidence-gc-and-memory-pressure.md`
4. `docs/234-partition-merge-and-split-brain.md`
5. `tests/test_rev0025_capgate_evidence_splitmerge.py`

The mental model:

```text
valid frame != valid namespace
valid namespace != valid capability
valid capability != admitted work
valid witness != immortal memory
valid latest head != safe merge after partition
```

rev0025 is still a design/prototype cube. It has no live I2P/SAM transport and no production DHT. Its purpose is to make the most dangerous local judgments executable before a live network can hide mistakes behind latency and churn.
