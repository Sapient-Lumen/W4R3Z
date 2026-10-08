# rev0079 search-epoch acknowledgement probe

Status: **pass**

```text
artifact tests: 78/78 passed
source invariants: 35/35 passed
compile checks: 21/21 passed
upstream units: 60 passed, 1 skipped
selected patch: None
```

A local applied acknowledgement is meaningful only after every fan-out request is prepacked and staged in network-owned output state. It remains weaker than socket write, delivery, or reconnect durability.

