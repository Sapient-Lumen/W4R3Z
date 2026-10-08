# Compact join and negative evidence

rev0049 added separate compaction lanes for witness evidence, raw audit receipts, redress GC, and scope journals. `compactjoin.py` exists because independent compaction can create a subtle failure:

```text
witness lane keeps summary A
audit lane keeps summary B
redress lane says hard negative exists
scope journal forgets the join
    -> stale public state looks clean after restart
```

`compactjoin.py` joins those reports at exact scope/request/subject and checks that live hard-negative digests survive in at least one retained lane. It also verifies that required component digests appear in the journal or current component set.

This is local memory hygiene, not consensus. It preserves hard evidence before memory pressure can erase it.
