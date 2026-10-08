# Witness repair and evidence gaps

Witness receipts are evidence, not quorum. rev0015 added aging and family caps; rev0016 tested repeated-round cache poisoning. rev0017 adds a small repair planner.

`witnessrepair.py` takes a `WitnessCacheSummary` and emits bounded next actions:

```text
ask_new_family
refresh_expired
quarantine_contradiction
preserve_only
```

The planner is intentionally small. If the summary is already fresh and diverse, it preserves only. If evidence is low-diversity or low-weight, it asks missing family hints. If evidence is self-contradicting, it refuses normal repair and tells the caller to preserve/quarantine evidence first.

This is a local planning surface. It does not create global reputation and does not decide truth.
