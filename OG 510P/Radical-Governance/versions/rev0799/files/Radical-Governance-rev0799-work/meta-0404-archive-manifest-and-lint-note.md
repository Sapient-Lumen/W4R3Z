# Meta 0404 — manifest and lint note

## Objective

Give the archive a small maintenance spine so future revisions can accumulate without becoming numerically sloppy or structurally inconsistent.

## Move made in this revision

Added:

- a compact `INDEX.md` for human scanability,
- a `Makefile` with a `lint` target,
- a lightweight `tools/lint_archive.py` checker.

## Why this matters

A governance archive can decay in ordinary ways long before its ideas decay:

- numbering drifts,
- required sections disappear,
- new notes stop matching house style,
- changelog and readme diverge,
- merge work becomes guesswork.

A tiny lint layer does not solve editorial judgment, but it does protect against dumb entropy.

## Current lint scope

The checker verifies:

- numbered archive filenames are unique and increasing,
- each numbered note starts with a matching heading,
- required sections exist,
- `README.md`, `CHANGELOG.md`, and `INDEX.md` are present,
- the current revision appears in both README and changelog.

## Next useful maintenance steps

- add optional front-matter fields for scope, domain, and cross-links,
- emit a machine-readable manifest for larger merges,
- generate a backlink report once the full corpus is present,
- add a quarantine marker for bold speculative notes that should not silently merge into canon.
