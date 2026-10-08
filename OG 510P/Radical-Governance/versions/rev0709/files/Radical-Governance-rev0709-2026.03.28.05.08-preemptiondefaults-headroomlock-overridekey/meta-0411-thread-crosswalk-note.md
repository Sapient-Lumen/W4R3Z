# Meta 0411 — Thread crosswalk and merge-oriented navigation

## Why this exists

As the continuation snapshot grows, simple chronological indexing stops being enough. The archive now spans recurring threads — contestability, monitoring, procurement, interoperability, accessibility, supplier dependence, and change control — that benefit from a second navigation layer.

## What changed

This revision adds a generated `THREADS.md` file plus `tools/build_threads.py`.

The thread crosswalk groups notes by inferred thematic tags from `ARCHIVE_INDEX.json`. This makes the compact bundle easier to:

- compare against other continuation bundles,
- merge back into a larger corpus,
- inspect for overbuilt versus underbuilt themes,
- find related notes without already knowing their revision number.

## Editorial rule

A continuation archive should stay legible in two directions:

1. **chronologically**, so revisions remain auditable; and
2. **topically**, so pattern families remain composable.

If future revisions add tags or refine inference logic, the crosswalk should remain lightweight and derivable rather than hand-curated.
