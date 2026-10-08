# Second adapter report

`second-adapter-report` turns the decision frame into a machine-readable recommendation.

## Why it exists

The repo already had a narrative decision frame, but not a repeatable artifact that combined:
- current support-record rollout priority
- current approved-source freshness
- explicit per-surface implementation heuristics

That made the second-adapter choice too easy to restate and too hard to audit.

## Inputs

- `SECOND-ADAPTER-MATRIX.json`
- `docs/support-records/*.md`
- `SUPPORT-SOURCE-LOCK.json`

## Main command

```bash
python scripts/second-adapter-report.py --pretty
```

## What it returns

- ranked candidate surfaces
- whether a candidate is currently eligible to lock as the next adapter
- why a surface is preferred, delayed, or blocked
- the suggested first lane and first workflow targets

## Current intended use

- treat the report as the default decision artifact before starting the next adapter
- refresh `SECOND-ADAPTER-MATRIX.json` when fresher official-surface observations or live evidence change the tradeoffs
- do not let the report replace live support bundles; it only chooses where to invest next
