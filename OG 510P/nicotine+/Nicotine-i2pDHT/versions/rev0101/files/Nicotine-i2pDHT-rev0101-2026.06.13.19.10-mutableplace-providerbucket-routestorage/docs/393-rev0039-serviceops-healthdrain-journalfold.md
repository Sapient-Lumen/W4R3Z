# rev0039 — serviceops-healthdrain-journalfold

rev0039 moves one boundary later than rev0038.  A service that passed continuity still needs repeated health windows, safe drain/stop semantics, and durable replay memory across restart.

The revision adds:

- `servicehealth.py` for post-continuity health windows under family, refusal, freshness, and metadata pressure.
- `servicedrain.py` for safe service drain/stop decisions that preserve withdrawals, receipts, open work, public announcement state, and hard negatives.
- `continuityjournal.py` for service-continuity replay memory that survives restart with monotonic links and hard-negative preservation.
- `serviceopsfold.py` for the current fold audit, preserving rev0038 `servicecontinuityfold` as predecessor history.

Core guess:

```text
A continuous service is not a healthy, stoppable, or restart-safe service until those claims bind to the same local memory boundary.
```

Nonclaims remain: no live I2P/SAM transport, no production DHT, no production garden-service protocol, no global reputation, no mutable-head consensus, no Sybil/anonymity guarantee, and no Nicotine+ patch.
