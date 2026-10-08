# Family-diversity and supersession refactor

rev0014 includes a concrete audit/refactor lane.

## Shared family diversity

`familydiversity.py` factors out the repeated shape that appeared in provider probing, witness receipts, churn frontiers, latency forge, and mutable-head lookup:

```text
sort candidates locally;
cap same-family evidence;
count family coverage;
notice monoculture;
do not call this independence.
```

The helper is intentionally small and does not retroactively rewrite every old module. New risk surfaces use it first. Older modules can migrate once the vocabulary stops moving.

## Supersession map

The cube is append-heavy. Some older revisions accidentally reused doc/ADR numbers or created near-duplicate module names. Deleting those files would damage wake-from-amnesia history, but leaving them as unexplained warnings made the audit noisy.

`HISTORICAL_SUPERSESSION.json` now names old paths and their active successors. `cubeaudit.py` loads this map and treats covered duplicate prefixes / near-duplicate module names as informational findings rather than warnings.

This is not cleanup theater. It is a way to distinguish active ambiguity from documented historical drift.
