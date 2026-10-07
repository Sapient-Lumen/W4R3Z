# Pruning Policy

This archive is a research archive, not a dump of every local compile artifact.

Rules:

1. Keep the canonical moving sources under `series/` textual and reviewable.
2. Keep already-published public conveniences under `published/` if they are part of the established public surface.
3. Keep generated index/report surfaces only where they clarify archive state (`index/`, `reports/`, selected `build/review_renders/`).
4. Do **not** ship local LaTeX build byproducts such as `.aux`, `.log`, `.out`, `.fls`, `.fdb_latexmk`, `.bcf`, `.run.xml`, `.bbl`, `.blg`, `.toc`, `.lof`, `.lot`, or `.synctex.gz`.
5. Do **not** ship compiled `paper.pdf` files inside moving `series/` trees; the source-of-truth there is the `.tex` file.
6. Ad hoc root/build compile checks may exist locally, but their byproducts should be pruned before packaging the archive.
7. Do **not** ship Python bytecode caches or interpreter leftovers such as `__pycache__/`, `.pyc`, or `.pyo`.
8. Do **not** ship per-paper review-render directories such as `series/.../renderNNN/`; keep those under `build/review_renders/` when they are the actual audit object.
9. When a transient or duplicated file is removed from the shipped bundle, record it in `PRUNED_TRANSIENT.paths`.

Current posture:

- published legacy papers may keep their convenience PDFs,
- `index/SERIES_INDEX.pdf` may remain as an index artifact,
- review-render PNGs may remain under `build/review_renders/` when they are the actual audit object,
- earlier revisions pruned 528 transient files from the shipped archive and removed the empty `publishing/__pycache__/` cache directory.
- this revision additionally pruned 16 lingering series review-render PNGs plus 5 `series/.../renderNNN/` directories that should not ship as moving-source state.
