# Support bundles

This tree holds named support-bundle manifests.

## States

- `candidate/` — shaped enough to review, but not yet ready to publish as a stronger support claim
- `hold/` — intentionally blocked from publication; useful evidence exists, but a named blocker still prevents stronger support language
- `published-ready/` — review says the bundle is coherent enough to cite for a stronger support claim
- `published/` — frozen support bundles that current support records may cite directly

## Rule

A support record may be backfilled from a named held/candidate bundle, but stronger tier promotion should prefer `published-ready` or `published` bundles.

## Current posture

GlassTTY now has its first canonical Claude reference bundle manifest, but it remains on hold until a live official-surface capture and route/state bundle exist.

## Queue vs citable truth

This tree is the review queue, not the citable support surface. `SUPPORT-PUBLIC-SURFACE.json` and `published-support-surface.py` answer the narrower question of what is safe to cite now.
