# Sibling broadcast replication pressure

The risky guess: if the DHT stores records only by asking the k closest nodes, a captured close neighborhood can silently become the record's reality.

rev0018 starts a local sibling-broadcast lab:

```text
candidate close siblings
  -> family-capped ask plan
  -> signed storage receipts / useful refusals
  -> contradiction and family-diversity analysis
  -> local replicated / continue / quarantine decision
```

## Important choices

- A signed storage receipt is evidence that a node claimed to store a record. It is not a proof that the record will remain retrievable.
- Useful refusal is not success, but it is positive capacity evidence. A garden that says “retry later” with bounded timing is more useful than a silent black hole.
- Accepted receipts from one family are not enough, even if the count is high.
- Same-node contradictory receipts are quarantine evidence.
- Close-window coverage matters. Receipts only from distant siblings mean the canonical region may still be captured, empty, or overloaded.

## Why this exists now

Mutable heads, tombstones, provider records, seed portfolios, and capability revocation heads all eventually depend on some storage layer. The cube should test whether its storage acceptance rules resist the dumbest capture patterns before the network code exists.
