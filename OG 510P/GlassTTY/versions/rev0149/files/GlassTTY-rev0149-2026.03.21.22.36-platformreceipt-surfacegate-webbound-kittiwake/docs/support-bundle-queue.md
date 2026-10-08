# Support bundle queue

`python scripts/support-bundle-queue.py --pretty` turns `docs/support-bundles/*/*.json` into one compact review surface.

## Purpose

The queue exists so GlassTTY can distinguish:

- evidence that is merely named,
- evidence that is intentionally blocked from publication,
- evidence that is ready to strengthen support language,
- and evidence that is already frozen/published.

## Why this matters

Support records should not have to carry the full publication state themselves.
A record can be backfilled from a held bundle while still refusing stronger claims until a review-ready or published bundle exists.

## Current posture

GlassTTY now has its first canonical held Claude reference bundle. That is progress because the evidence is finally named and inspectable. It is also intentionally conservative because the archive still lacks a current live official-surface Claude bundle.

## Important split

The queue is not the same thing as the citable support surface. Use `published-support-surface.py` when you need to know what is safe to cite **now**.
