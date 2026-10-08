---
revision_current: rev0373
generated_at: 2026-06-18T18:20:00Z
title: MA row-contract workbench audit
status: audit_refactor_substantive_row_contract_added
---

# MA row-contract workbench audit — rev0373

Problem found: rev0372 created source routes, but not the row contract needed to stop a route-only or aggregate-only pass. The Social Security/Medicare maturity counts were also stale relative to the live evidence ledgers.

## Corrections

- Added `cases/social-security-medicare-claim-security-rev0318-ma-contract-claim-security-workbench-rev0373.json`.
- Added 7 noncertifying locator-bound evidence records.
- Added 6 CMS source routes, S591-S596.
- Resynced the case maturity row to live evidence counts.
- Added `tools/audit_ma_row_contract_workbench.py` and validator checks.

Certification after audit: **not certified current**.
