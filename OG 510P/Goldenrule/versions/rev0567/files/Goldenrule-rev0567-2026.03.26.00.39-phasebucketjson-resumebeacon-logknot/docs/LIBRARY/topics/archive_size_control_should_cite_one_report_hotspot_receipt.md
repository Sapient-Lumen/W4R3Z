# Archive size control should cite one report hotspot receipt

The package receipt now proves that the tree is clean, chain-consistent, and small enough to package safely.
What it does not say by itself is which retained report families are actually driving the next round of archive growth.

## Why this matters

The current archive already knows that `artifacts/reports` is the main retained growth surface.
A future inheritor should not have to reopen the full archive-size profile just to answer the practical question "which report families should I compact first if the archive starts growing again?"

## What to keep

Keep one tiny hotspot receipt outside `artifacts/reports` that:

1. aligns with the standing package receipt,
2. ranks the largest retained report families and individual report files,
3. exposes how concentrated the report bucket is in its top hotspots, and
4. names a short list of first compaction targets.

That gives the inheritor a small citation surface for archive-shaping decisions without creating another report-pair family.

## Operational rule

Build the hotspot receipt after the package receipt passes.
When the archive needs more size discipline, cite the hotspot receipt first and compact the ranked report families before adding new report fanout nearby.
