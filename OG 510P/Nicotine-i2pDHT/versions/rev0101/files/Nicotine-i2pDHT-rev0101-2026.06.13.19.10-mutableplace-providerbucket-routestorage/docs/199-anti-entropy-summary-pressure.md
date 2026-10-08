# Anti-entropy summary pressure

Lookup answers are point observations.  A useful DHT also needs periodic reconciliation: what do neighbors and gardens think is current for mutable heads, tombstones, provider ledgers, and custody facts?

`antientropy.py` models small signed summaries.  They are short-lived and local.  They do not create consensus.  A summary can cause the local node to request missing data, ask for more family diversity, preserve fork evidence, or quarantine rollback pressure.

Important rule:

```text
Anti-entropy summaries request repair; they do not decide truth.
```

The riskiest test added in this lane is tombstone-first reconciliation.  A newer tombstone should be requested before convenient stale cache evidence can resurrect a withdrawn or compromised thing.
