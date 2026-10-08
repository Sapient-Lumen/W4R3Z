# Exit journal restart memory

`exitjournal.py` adds a tiny append-only local journal for operator/service-control facts.

The journal carries signed entries for:

- operator intent;
- breaker state;
- service exit;
- router stop shadow;
- session resume;
- profile GC;
- hard negatives.

It rejects bad signatures, replay, rollback, same-sequence forks, previous-link mismatch, service/scope/request drift, sequence gaps, and hard-negative drops.

The key rule:

```text
Local memory is still protocol data after restart.
```

The journal is not a production database. It is a pressure fixture for the eventual database/journal layer.
