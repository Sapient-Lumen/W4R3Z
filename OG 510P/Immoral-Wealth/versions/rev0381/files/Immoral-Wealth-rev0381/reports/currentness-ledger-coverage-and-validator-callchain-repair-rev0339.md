---
revision_current: rev0355
status: active_report
claim_kind: audit_refactor
---

# rev0339 — currentness-ledger coverage and validator callchain repair

## Problem

rev0338 passed validation while two hidden invariants were not actually closed:

1. Nineteen active scoreboards had no `currentness-ledger` case row, which meant their refresh deadlines were visible in the scoreboard but absent from the release-level currentness control.
2. `tools/validate_archive.py` defined rev0327-rev0338 hardening checks, but `main()` stopped after rev0332 and therefore did not execute the newer target checks.

## Changes

- Added currentness rows for 19 active cases.
- Added a global validator invariant requiring every active scoreboard to have a currentness-ledger row and matching refresh date.
- Added a global validator invariant requiring every non-`not_applicable` gate-inventory row to carry `source_ids`.
- Repaired the validator callchain so rev0327-rev0338 hardening checks execute again.
- Patched historical audit references so old checks read their own historical audit files rather than brittle current-release audit filenames.
- Added S487-S489 to strengthen procurement and UK offshore-property authority.
- Corrected source-fit metadata for S162, S169, S172, S173, S174, and S183.

## Result

Remaining missing currentness rows: `0`

Remaining non-not-applicable gate-inventory rows without source anchors: `0`
