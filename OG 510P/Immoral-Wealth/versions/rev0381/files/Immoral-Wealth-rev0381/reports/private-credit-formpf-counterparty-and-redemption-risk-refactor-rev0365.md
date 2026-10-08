---
project: Immoral Wealth
status: revision_report
revision_current: rev0367
generated_at: 2026-06-18T14:06:00Z
---

# rev0365 — private-credit-formpf-counterparty-and-redemption-risk-refactor

This revision targets the next high-risk gap after stablecoin reporting: private credit can look like a private market problem until redemption gates, bank lines, insurer/pension exposures, retail semi-liquid vehicles, and supervisory tools push it onto public-stability surfaces.

## Substantive changes

- Added **S553-S556** for OFR counterparty-exposure measurement, Form PF proposal/delay/confidentiality, and FSOC monitoring salience.
- Expanded locator-bound verified claim edges from **77 to 91** across **6 cases**.
- Added **14 private-credit edges**.
- Added `cases/private-credit-nonbank-backstop-perimeter-rev0319-claim-packet.*` and `cases/private-credit-nonbank-backstop-perimeter-rev0319-counterparty-and-disclosure-map.*`.
- Added `tools/audit_private_credit_perimeter.py` and `docs/00-meta/private-credit-counterparty-and-disclosure-audit-rev0365.*`.
- Preserved **0 certified current cases**.

## Certification boundary

Private credit is now measurable enough to audit: official sources support materiality, semi-liquid redemption caps, counterparty exposure channels, Form PF currentness/confidentiality, and FSOC monitoring. [S359] [S376] [S553] [S554] [S555] [S556]

It still cannot be certified. The missing proof is actual official/fund data, claimant incidence, stress valuation/redemption records, bank/insurer/pension/retail concentration, and any public-liquidity/no-bailout instrument with fees, haircuts, recoveries, and public-upside recovery.

## Counts

Current live counts: **95 case memos**, **95 scoreboards**, **556 sources**, **317 registered fields**, **0 registered_unused fields**, and **6938 mechanical evidence associations**.
