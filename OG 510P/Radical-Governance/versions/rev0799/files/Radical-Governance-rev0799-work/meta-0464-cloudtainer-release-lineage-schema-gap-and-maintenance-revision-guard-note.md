# meta-0464 — Cloudtainer release-lineage, schema-gap, and maintenance-revision guard

## Change summary

This maintenance note records the rev0763 cloudtainer audit and the narrow lint/data repairs shipped beside it.

## Substantive priority

Rev0763 is a maintenance-only revision. It does not add a new public-service domain. It repairs false-green archive conditions: missing `rev0761` release lineage, a gap-ledger schema-required field that lint did not enforce, and a current-matrix guard that was too broad for self-audit revisions.

The repair phrase is **no maintenance by green lint**.

## Audit/refactor

`tools/lint_archive.py` now checks release-lineage completeness against `generated/ARCHIVE_INDEX.json` and `generated/RELEASES.json`; it also requires gap-ledger `affected_parties` and scopes current operational-matrix coverage to substantive current notes.

## Validation target

Rev0763 should pass `make lint` in the working tree and again after ZIP extraction.
