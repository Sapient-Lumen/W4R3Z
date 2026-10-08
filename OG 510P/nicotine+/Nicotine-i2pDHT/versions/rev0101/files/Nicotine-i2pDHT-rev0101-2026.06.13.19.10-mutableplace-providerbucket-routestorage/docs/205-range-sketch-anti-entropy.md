# Range-sketch anti-entropy

`rangesketch.py` turns rev0022's anti-entropy summaries into a more scalable guess: compare compact roots for XOR keyspace regions before requesting exact records.

The sketch is deliberately not consensus. It signs observations such as:

```text
kind = mutable_head | provider_ledger | tombstone | store_custody
region_bits / region_prefix
sequence
root_digest
item_count
tombstone_count
source_family
```

Local behavior:

- matching diverse roots mean the range is locally in sync;
- newer diverse roots request exact repair objects;
- tombstone-range mismatches are repaired before convenience data;
- same-sequence different roots are fork pressure;
- repeated lower sequences are stale replay pressure;
- one-family sketch monoculture keeps asking for more evidence.

The design borrows the old anti-entropy intuition of comparing summaries by range, but refuses to let a digest root decide truth alone. Roots are repair hints.
