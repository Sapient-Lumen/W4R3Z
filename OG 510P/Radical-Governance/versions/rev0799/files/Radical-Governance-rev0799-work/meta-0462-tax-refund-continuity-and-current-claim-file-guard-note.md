# meta-0462 — Tax refund continuity and current claim-file guard

## Change summary

This maintenance note records the rev0761 tax/refund continuity packet and the narrow lint refactor added beside it.

## Substantive priority

Rev0761 adds tax filing, refunds, refundable credits, ITIN, identity theft, direct deposit, offsets, free filing, and Taxpayer Advocate continuity because the archive had benefits, food, housing, veterans, immigration, identity, and payment-redress packets but lacked a direct tax-relief packet.

The repair phrase is **no tax relief by return row**.

## Audit/refactor

`tools/lint_archive.py` now checks that `metadata/claims.json` declares exactly the current substantive note files in `current_note_files`. This catches a fresh-packet drift mode where claims can be present but the ledger's current-file header silently points at the previous revision.

## Validation target

Rev0761 should pass `make lint` in the working tree and again after ZIP extraction.
