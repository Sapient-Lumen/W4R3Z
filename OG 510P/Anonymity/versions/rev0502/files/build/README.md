# Build Artifacts

This directory holds generated review-time and compile-time artifacts that should not clutter the shipped repo root.

## Subdirectories

- `root_latex/` — transient LaTeX byproducts produced from ad hoc root-level compile checks.
- `review_renders/` — rendered first-page PNGs and render batches used during cautious review turns.

- `index_latex/` — transient compile byproducts from rebuilding `index/SERIES_INDEX.tex`.

These files may be useful for audit/debugging, but they are not canonical paper sources. Transient compile byproducts from `root_latex/` and `index_latex/` should usually be pruned before a release bundle is shipped; see `PRUNING_POLICY.md`.

Do not confuse files in this directory with compact control surfaces; use `publishing/rebuild_archive_surfaces.py` when compact reports/manifests need regeneration.
