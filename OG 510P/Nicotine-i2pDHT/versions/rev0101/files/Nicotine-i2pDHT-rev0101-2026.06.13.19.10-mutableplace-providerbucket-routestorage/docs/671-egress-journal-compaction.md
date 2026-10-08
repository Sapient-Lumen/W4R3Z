# Egress journal compaction

The egress journal is the restart-memory surface after late ACKs, retry settlement, and withdraw repair. It can compact ordinary terminal evidence, but it must not drop contradictions.

The riskiest case is:

```text
late original ACK present
+ retry terminal delivered present
+ compaction summary present
- contradiction entry missing
```

That becomes `quarantine_dropped_contradiction`. Compaction is allowed only when the journal has enough exact-boundary entries, diversity pressure, and no required contradiction has been erased.
