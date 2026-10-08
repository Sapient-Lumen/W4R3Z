---
status: active_protocol
claim_kind: valuation_protocol
route_role: measurement_uncertainty_core
canonical_anchor: false
route_refs:
- measurement_uncertainty_core
- floor_core
- case_calibration_core
supersedes: null
depends_on:
- ../10-framework/asset-composition-and-control.md
- ../10-framework/present-accessibility-and-lock-up-of-claims.md
source_refresh_due: 2026-12-31
---

# Asset valuation, liquidity, and control haircuts

The archive already rejected face-value treatment of locked or inaccessible claims. rev0308 adds a more explicit valuation rule: **wealth counts differently depending on liquidity, control, pledgeability, risk, and exit cost**.

## Haircut families

| Asset or claim | Main haircut question |
|---|---|
| owner-occupied housing | Can the person borrow, downsize, sell, or repair without losing shelter? |
| pension wealth | Is it vested, portable, inflation-protected, and person-controlled? |
| private business equity | Is valuation observable; can the owner sell; who has control? |
| private funds / private markets | What are lockups, fees, valuation marks, and investor access constraints? |
| trusts/foundations/family entities | Who can direct distributions or control assets? |
| social housing or tenancy rights | Are rights secure, portable, and sufficient to substitute for ownership? |
| public claims | Are they legally enforceable, funded, and claimable at the threshold moment? |

## Why this matters

At the top, valuation uncertainty can hide concentrated control. Forbes-style rich-list methods must estimate private businesses using multiples, profits, revenue, debt assumptions, and market comparables; those are useful clues but not registry-grade measurements.[S159] Research on heterogeneous returns also shows that assuming uniform returns within asset classes can distort top-wealth estimates.[S160]

At the bottom and middle, face-value assets can overstate security. A household can have home equity but no repair buffer, pension wealth but no present cash, or a title interest that cannot be sold or mortgaged because heirs or probate questions remain unresolved.

## Operational rule

Use haircuts whenever a case asks whether wealth is a **floor** or a **foothold**. Do not use haircuts to excuse top-tail concentration. At the top, valuation uncertainty usually creates audit duty; at the bottom, it usually reduces usable security.

This asymmetry is intentional. The archive cares about dependency, closure, and rule. Overstating lower-half security creates false passes; understating top-tail control creates false comfort.
