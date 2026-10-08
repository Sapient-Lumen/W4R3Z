# Proof obligation — rev0050

rev0050 proves only local invariants:

```text
accepted outbox + accepted dry-run + accepted SAM trace + accepted journal
  -> may create a local drain/commit receipt if exact-boundary checks pass

accepted drain + accepted SAM trace + accepted egress
  -> may create a local SAM canary if exact-boundary checks pass

accepted witness/audit/redress/journal compaction
  -> may be treated as safe only if live hard negatives survive the join
```

It does not prove a network write, DHT truth, global consensus, or anonymity.
