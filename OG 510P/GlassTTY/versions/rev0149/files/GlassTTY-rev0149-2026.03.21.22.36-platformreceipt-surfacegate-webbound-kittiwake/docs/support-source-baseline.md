# Support-source baseline

`support-source-baseline` freezes the current approved-source hierarchy and the source refs currently attached to support bundles.

## What it answers

- Which approved first-party or vendor-runtime sources exist for each official surface?
- Which support bundles already cite those sources?
- Which publishable bundles still lack required source refs?
- Which source refs are unknown or outside the approved hierarchy?
- Which approved sources or the lock itself have gone stale under the current review-age policy?

## Outputs

- root snapshot: `SUPPORT-SOURCE-BASELINE.json`
- latest capture bundle: `validation/latest/support-source-baseline/`
- capture history: `validation/support-source-baseline-captures.json`

## Command

```bash
python scripts/support-source-baseline.py --pretty
```

## Current use

The source baseline does **not** publish support bundles and does **not** replace live workflow evidence. It gives the support publish gate one more fail-closed question: what approved authority basis is attached to this bundle right now, and how fresh is that authority under the current review policy?
