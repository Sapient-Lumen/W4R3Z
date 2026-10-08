---
revision_current: rev0374
generated_at: 2026-06-18T18:42:00Z
title: MA appeal-burden public pilot audit
status: audit_refactor_public_pilot_added_not_certifying
---

# MA appeal-burden public pilot audit — rev0374

Problem found: rev0373 defined the row contract, but the cube still lacked a quantified public pilot that made the appeal-burden mechanism visible.

## Corrections

- Added the public MA appeal-burden pilot file.
- Added 7 noncertifying locator-bound evidence records.
- Added 8 explicit mechanical public-pilot evidence routes.
- Added `tools/audit_ma_appeal_burden_pilot.py`.
- Refactored `tools/audit_ma_row_contract_workbench.py` so future revisions do not fail only because the workbench filename is revision-specific.

Certification after audit: **not certified current**.
