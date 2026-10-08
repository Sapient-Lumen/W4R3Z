# Delta-sketch repair pressure

rev0030 adds two anti-entropy repair surfaces:

- `deltasketch.py` for compact bucketed summaries over provider/head/tombstone/custody/policy items;
- `rangesetdelta.py` for range-set delta summaries over regional record sets.

The rule remains:

```text
summary mismatch requests repair; it does not declare truth
```

Both sketches test same-sequence forks, stale replay, source-family monoculture, and tombstone-first repair. Small deltas request exact repair. Wide deltas can ask for child-range repair. Tombstone deltas are prioritized so stale convenience data does not resurrect withdrawn or compromised state.

These sketches are intentionally simple. They exist to test pressure semantics before choosing a production reconciliation primitive.
