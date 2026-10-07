# Published Papers

This directory contains papers that have been explicitly frozen for public release.

## Required naming format

Every new published paper must live in a directory named exactly:

`YYYY.MM.DD - Anonymity: The Foobar Title Goes Here Please`

Inside that directory, the canonical LaTeX source file must be named exactly:

`YYYY.MM.DD - Anonymity: The Foobar Title Goes Here Please.tex`

## Wiki-link rule

All references to a published paper should target the basename in wiki-link syntax:

`[[YYYY.MM.DD - Anonymity: The Foobar Title Goes Here Please]]`

## Canonical artifact rule

The `.tex` file is the canonical published artifact.
A PDF may exist, but the release decision freezes the LaTeX source.

## Legacy note

Some older published entries in this repository use legacy internal directory names.
Their canonical public wiki links are listed in `published/LEGACY_PUBLISHED_LINKS.md`.
They are left in place to avoid accidental breakage.
Future turns may migrate them individually only with an explicit crosswalk and a preservation plan for public links.


## Classification aid

See `published/PUBLICATION_CLASSIFICATION.md` before assuming that every file stored under `published/` is also an approved canonical public wiki target.

## Quick boundary helpers

- `CITATION_HEADS.md` — compact current citation-head register with counts and warnings
- `PUBLIC_SURFACE.json` — machine-readable description of the stable published-facing surface
- `reports/archive_surface_coherence.json` — latest agreement check between citation/classification/public-surface summaries

- `reports/lifecycle_gate_status.json` — stage-aware reminder of whether the archive is merely in reentry/audit posture or actually near publication execution
