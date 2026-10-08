# meta-0461 — Immigration status continuity and current claim/case source parity

## Change summary

This maintenance note records the rev0760 packet and the small lint refactor added beside it.

## Substantive priority

Rev0760 adds immigration/asylum/status continuity because the archive had digital-status migration and border/watchlist materials but lacked a person-level packet for USCIS, EOIR, asylum, work authorization, SAVE, address, notice, portal, and downstream benefit/license continuity.

The repair phrase is **no status by receipt row**.

## Audit/refactor

`tools/lint_archive.py` now checks that current-revision claims and current applied-case packet entries use the same source-key set as the current note metadata. This catches a real drift mode: a new packet could previously pass with correct note metadata and source catalog entries while its claim ledger or case-packet row silently carried stale or partial source keys.

## Validation target

Rev0760 should pass `make lint` in the working tree and again after ZIP extraction.
