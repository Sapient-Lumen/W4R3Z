# meta-0463 — Consumer finance continuity and current source-provenance guard

## Change summary

This maintenance note records the rev0762 consumer-finance continuity packet and the narrow lint refactor shipped beside it.

## Substantive priority

Rev0762 adds consumer finance, credit reporting, debt collection, bank/prepaid account, EFT/payment-error, complaint, and regulator-routing continuity because the archive had payment, tax, benefit, food, housing, broadband, and identity packets but no direct account/report/debt continuity surface.

The repair phrase is **no financial access by account row**.

## Audit/refactor

`tools/lint_archive.py` now checks that source keys first appearing in current-revision notes have `metadata/source_health.json` entries whose `first_added_revision` equals the current revision. This catches a fresh-source provenance failure without forcing historical source-health backfill.

## Validation target

Rev0762 should pass `make lint` in the working tree and again after ZIP extraction.
