# Meta 0405 — machine-readable manifest note

## Objective

Make compact continuation bundles easier to verify, diff, and merge by adding a generated manifest that records the archive contents in machine-readable form.

## Move made in this revision

Added:

- `tools/build_manifest.py`
- generated `MANIFEST.json`
- Makefile wiring so `make lint` refreshes the manifest before checking integrity

## Why this matters

A continuation archive is easier to trust when a future maintainer can quickly see:

- which files were present,
- which numbered notes were included,
- what top-level maintenance files existed,
- which revision the package claims to be.

This does not replace editorial review, but it reduces merge ambiguity and makes accidental omissions easier to spot.

## Current manifest scope

The manifest records:

- current revision identifier,
- top-level files,
- numbered archive notes and their titles,
- meta notes,
- tool scripts,
- generation timestamp in UTC.

## Next useful maintenance steps

- include lightweight hashes for stronger bundle verification,
- emit cross-link hints once the full corpus is available,
- add canon versus quarantine markers for speculative notes,
- produce a revision-to-revision diff summary automatically.
