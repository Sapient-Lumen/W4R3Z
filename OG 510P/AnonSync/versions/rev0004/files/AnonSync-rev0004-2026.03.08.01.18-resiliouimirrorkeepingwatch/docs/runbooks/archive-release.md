# Archive Release Runbook

## Purpose

Produce a clean zip archive for the current repository revision.

## Steps

1. Update docs and metadata.
2. Run:
   - `python scripts/validate_repo.py`
   - `python scripts/generate_context_pack.py`
3. Update `CHANGELOG.md`.
4. Confirm revision metadata in `metadata/archive-manifest.json`.
5. Run:
   - `python scripts/archive_release.py`

## Archive naming

`AnonSync-rev####-YYYY.MM.DD.HH.MM-codename.zip`

## Exclusions

Release zips should exclude:
- `__pycache__`
- local caches
- prior release zips
- transient artifacts unless explicitly needed
