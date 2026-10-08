# Standing rematch-world benchmark seed should be rebuild-audited before fill work begins

The retained rematch-world benchmark seed is intentionally self-contained: it already embeds the compact decision bundle and the seven copied handoff sections that explain how the first endogenous benchmark should be interpreted.

That convenience creates a quiet risk for the inheritor. A later session can accidentally drift one copied handoff or the standing seed template while still leaving the archive *looking* coherent, because the seed is large and the copied sections are only a small subset of it.

The fix should stay small.

## What to retain

Retain one tiny audit receipt that proves two things at once:

1. the standing seed still rebuild-matches the current seed builder, and
2. each copied frozen section in the standing seed still hash-matches its standalone source handoff or standing decision contract.

## Why this is better than wider notes

The inheritor does **not** need another narrative walkthrough of the seed.
They need one compact proof that the fill baseline is still trustworthy before they begin world-dependent edits.

That receipt keeps the archive citation-first:

- cite the standalone handoff examples and the standing decision contract,
- prove the copied sections still match,
- avoid recopying the full seed or reopening several proxy reports every session.

## Operational rule

Run the frozen-handoff audit before new fill work begins whenever any copied handoff, the standing decision contract, or the seed builder changes.
If it fails, rebuild the standing seed first; do not start world-dependent edits from a silently drifted baseline.
