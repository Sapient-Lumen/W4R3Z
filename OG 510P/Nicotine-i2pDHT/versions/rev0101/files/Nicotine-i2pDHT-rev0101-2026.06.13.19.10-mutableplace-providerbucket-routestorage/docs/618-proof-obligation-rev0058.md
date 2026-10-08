# Proof obligation — rev0058

A future implementation must prove at least:

```text
terminal markers cannot be forged or replayed
terminal markers cannot appear while retry/dead-letter is required
retry tickets always carry dead-letter lineage
retry tickets cannot change idempotency boundary
prune plans cannot delete hard negatives
prune plans cannot delete pending retry/dead-letter evidence
```

The current cube only tests deterministic no-network toy surfaces for these obligations.
