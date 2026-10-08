---
project: Immoral Wealth
status: revision_report
revision_current: rev0367
generated_at: 2026-06-18T14:06:00Z
---

# rev0364 — stablecoin reporting forms and currentness-watch refactor

This revision targets the top risk from rev0363: the stablecoin case had a statutory perimeter but could still stall at “issuer data needed.” Rev0364 binds the actual proposed reporting architecture.

## Substantive changes

- Added **S549-S552** for OCC Bulletin 2026-24, OCC PS-01 weekly instructions, OCC PS-02 quarterly instructions, and FDIC FIL-11-2026.
- Expanded locator-bound verified claim edges from **65 to 77** across **5 cases**.
- Added **12 stablecoin reporting-form/currentness edges**.
- Added `cases/stablecoins-money-market-treasury-liquidity-backstop-rev0319-issuer-reporting-data-map.*`.
- Added `tools/audit_currentness_watchlist.py` and `docs/00-meta/currentness-watchlist-audit-rev0364.*`.
- Preserved **0 certified current cases**.

## Certification boundary

OCC PS-01/PS-02 and FDIC proposed requirements reduce measurement debt, but they do not certify the case. The decisive missing items are final forms/rules, OMB/PRA disposition, actual issuer filings or public aggregate disclosures, custody/redemption/insolvency priority, public-liquidity terms, and public-upside recovery. [S549] [S550] [S551] [S552]

## Counts

Current live counts: **95 case memos**, **95 scoreboards**, **552 sources**, **317 registered fields**, **0 registered_unused fields**, and **6893 mechanical evidence associations**.
