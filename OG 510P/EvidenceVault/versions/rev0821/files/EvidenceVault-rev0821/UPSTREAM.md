# Upstream inputs

This unified archive is a **curated, de-duplicated** consolidation of the upstream project archives.

To keep the unified release compact, the upstream zip files themselves are **not embedded** here.
Instead, their digests are recorded in `UPSTREAM_INPUTS.sha256`, and the extracted/curated contents are integrated under `sources/`, `schemas/`, `artifacts/`, `certs/`, `renders/legacy_pdfs/`, and `papers/`.

## Zip inputs (sha256)

See `UPSTREAM_INPUTS.sha256`.

## Redactions policy

- Obvious private keys / secret signing keys are removed from imported trees.
- The removed paths are listed in `REDACTIONS.paths` (relative to archive root).
- Public certificates, public keys, and signed statements are retained.
