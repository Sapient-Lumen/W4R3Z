---
status: active
claim_kind: revision_report
route_role: archive_governance_core
route_refs:
- archive_governance_core
- household_market_extraction_core
- certification_core
revision_current: rev0355
source_refresh_due: 2026-12-31
---

# rev0334 household-market-extraction current-law hardening and seed-class burndown

## Why this was next

After rev0333, all scoreboards were active, but 25 active scoreboards still carried seed calibration labels. The riskiest remaining cluster was Gate 16 because product law, enforcement posture, and household threshold timing can change faster than the case prose.

## Cases hardened

- `bnpl-earned-wage-credit-visibility-rev0314`
- `united-states-auto-finance-repossession-rev0314`
- `united-states-consumer-finance-fee-drain-rev0314`
- `united-states-childcare-cost-time-wealth-rev0314`
- `oecd-long-term-care-asset-spenddown-rev0314`

## Substantive changes

The BNPL/EWA case now distinguishes product usefulness from aggregate obligation visibility. It requires total-obligation, fee/tip, refund/dispute, payroll-priority, and credit-file/collection-transition evidence before comfort scoring.[S264][S265][S272]

The auto-finance case now treats the vehicle as mobility collateral. Repossession, negative equity, add-ons, deficiency balances, and transit-substitute weakness are threshold harms, not ordinary consumer-credit details.[S260][S266][S267][S280]

The consumer-fee case now separates sectoral all-in-price wins from the broader fee stack. Overdraft, credit-card late fees, high-cost credit, account rails, subscription cancellation, and state-law variation now carry distinct evidence burdens.[S260][S262][S263][S268][S269][S270][S271][S279]

The childcare case now treats care as a work/savings conversion rail. Local price, supply, hours fit, subsidy conversion, and maternal labor-force evidence are required before the case can relax Gate 16.[S273][S274][S275][S276]

The long-term-care case now treats care need as a late-life asset-liquidation and family-labor threshold moment. Housing, pensions, and family transfers must be netted against care costs, access limits, informal care, and means-test/home-equity design.[S277][S278]

## Refactor

S279 was relabeled from `official` to `nonprofit_research` and from direct operative authority to context. It remains useful for state-law triage but cannot be used as official current law without validation against statutes or regulators.

Remaining active seed-calibration labels after this pass: 20.

<!-- current_revision: rev0334; codename: household-market-extraction-current-law-hardening-and-seedclass-burndown -->
