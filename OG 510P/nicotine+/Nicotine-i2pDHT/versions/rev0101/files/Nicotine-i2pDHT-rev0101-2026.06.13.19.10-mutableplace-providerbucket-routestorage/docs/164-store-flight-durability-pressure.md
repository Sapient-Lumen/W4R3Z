# Store-flight durability pressure

A store flight is the local admission surface around accepting small DHT records into a garden node. The risky failure is making STORE a vague yes/no. A useful garden should decide under explicit budgets, preserve high-value control-plane records, refuse overload clearly, and emit signed custody receipts when it accepts custody.

rev0019 models:

```text
candidate record -> validate liveness/proof/tombstone pressure
                 -> apply source-family and bulk-family caps
                 -> protect control-plane reserve
                 -> evict lower-priority sloppy/provider cache when safe
                 -> sign custody receipt for accepted records
```

Tombstones, mutable heads, witness receipts, and contact leases are treated as control-plane records. Bulk provider records and sloppy-cache records are useful, but they should not crowd out the steering wheel of the DHT.
