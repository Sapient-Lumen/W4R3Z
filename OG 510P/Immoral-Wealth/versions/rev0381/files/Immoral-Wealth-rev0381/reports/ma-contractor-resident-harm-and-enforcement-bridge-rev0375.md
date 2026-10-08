---
revision: rev0375
base_revision: rev0374
generated_at: 2026-06-18T19:03:00Z
codename: ma-contractor-resident-harm-and-enforcement-bridge
status: active_release_report
---

# ma-contractor-resident-harm-and-enforcement-bridge — rev0375

Rev0375 keeps the MA work substantive. Rev0374 showed appeal burden; rev0375 prevents that burden from being averaged away by adding contractor, resident-vulnerability, audit, enforcement, and CY2026 plan-obligation dimensions.

## What changed

- Added 3 official CMS sources: `S597` program audits, `S598` enforcement actions, and `S599` CY2026 final-rule obligation fields.
- Added 8 locator-bound evidence records: `VCEDGE-rev0375-0194` through `VCEDGE-rev0375-0201`.
- Added 4 explicit mechanical bridge route rows for the Social Security/Medicare case.
- Added `cases/social-security-medicare-claim-security-rev0318-ma-contractor-resident-harm-enforcement-bridge-rev0375.json` and `.md`.
- Added `tools/audit_ma_contractor_resident_harm_enforcement_bridge.py`.

## Substantive finding

The next minimum viable MA row is now narrower and harder to fake: one SNF or other service-specific contract-month row must retain contractor/delegated-entity identity, nursing-home-resident/post-hospital status, request/denial/appeal/overturn counts, notice, approved-authorization reopening, concurrent decision, time-to-care, service furnished, beneficiary/provider restoration, program-audit result, enforcement action, quality context, and RADV/payment context.

## Certification boundary

Still **not certified current**. CMS audit and enforcement rails are accountability surfaces, not proof of beneficiary remedy. CY2026 rule obligations are not observed compliance. Contractor and nursing-home-resident metrics are decisive warning rows, not complete request-level outcomes.
