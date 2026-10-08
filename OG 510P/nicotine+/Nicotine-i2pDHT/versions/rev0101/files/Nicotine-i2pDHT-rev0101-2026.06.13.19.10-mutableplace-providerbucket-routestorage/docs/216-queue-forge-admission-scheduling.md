# Queue forge admission scheduling

Admission is not only a batch decision. Garden nodes will receive work over time with awkward latency, overload, and mixed value:

```text
head_watch
witness_query
seed_gate
tombstone_repair
store_repair
provider_bulk
```

rev0024 adds `queueforge.py`, which tests stream caps, source-family quotas, reserve slots for survivor work, latency deadlines, bulk deferral, family-flood quarantine, and signed useful-refusal receipts.

The design guess is that garden nodes need a polite queue vocabulary before they need a sophisticated live transport. If a garden can say “not now, retry later” with a signed bounded receipt, the network gets better behavior than silent drops or unbounded generosity.
