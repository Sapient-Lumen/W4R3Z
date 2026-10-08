# Refresh truth surfaces

`python scripts/refresh-truth-surfaces.py --pretty` is the one-shot command for rebuilding the repo's main current-state truth stack.

## What it refreshes

- opening-surface conformance
- readiness report capture
- control-plane report capture
- install receipt capture
- support-surface capture
- operator handoff bundle
- truth-surface register
- truth-surface warning ledger
- validation artifact inventory
- support-bundle queue capture
- support-bundle contract
- revision-receipt conformance

## Why this exists

This command is the smallest durable fix for a real archive problem: frozen `validation/latest/*` bundles can otherwise survive across revisions even when their payloads still identify an older root.

Refreshing the truth surfaces after a meaningful archive update keeps the packaged revision's current-state evidence aligned with the revision that actually ships.

## Command

```bash
python scripts/refresh-truth-surfaces.py --pretty
```

The refresh pass now also keeps the support-bundle queue, support-bundle contract, archive self-description, and validation bucket summary current, not just the core runtime/support truth surfaces.


This pass also refreshes the published-support surface and `SUPPORT-PUBLIC-SURFACE.json`.
