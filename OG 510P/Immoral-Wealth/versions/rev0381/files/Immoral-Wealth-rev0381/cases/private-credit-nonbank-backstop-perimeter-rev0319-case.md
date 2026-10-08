---
status: active_case
claim_kind: case_memo
route_role: public_balance_sheet_core
canonical_anchor: false
route_refs:
- public_balance_sheet_core
- case_calibration_core
supersedes: null
depends_on:
- ../docs/20-program/gate-20-public-balance-sheet-register-and-subgates.md
- ../docs/20-program/public-balance-sheet-seniority-waterfall.md
source_refresh_due: 2026-09-30
case_pressure: rev0326_gate20_backstop_burndown
---

# Private credit and nonbank backstop perimeter case — active Gate 20 case

## Verdict

**Correction required.** This case is now an active nonbank-public-backstop case rather than a seed warning. The breach is not merely that private credit is large; it is that loss visibility, liquidity promises, bank financing, insurer/pension exposure, retail semi-liquid vehicles, and borrower-employment channels can move private credit stress onto public-stability or ordinary-claimant surfaces before any explicit bailout is named. [S359] [S376]

## Evidence hardening

The FSB private-credit report keeps the case live because private credit at its current size and scope has not been tested in a severe downturn and because bank, insurer, pension, cross-border, leverage, liquidity-mismatch, valuation, and data-gap channels can amplify stress. [S376]

The Federal Reserve's May 2026 Financial Stability Report makes the U.S. channel concrete. It estimates private credit loans at about $1.4 trillion, or roughly 10 percent of total U.S. nonfinancial corporate debt and about one-third of below-investment-grade debt excluding bank loans. It also identifies semi-liquid vehicles—perpetual-life BDCs and interval funds—as a retail-facing liquidity-transformation channel, notes increases in redemption requests and redemption caps, and describes continuing bank lending to private-credit funds and BDCs. [S359]

## Gate 20 subgate findings

- **20C_contingent_liabilities_guarantees — blocked:** The case cannot certify comfort while bank commitments, insurer/pension exposures, semi-liquid retail vehicles, private valuation, leverage, and borrower-credit losses remain incomplete in the public map. [S359] [S376]
- **20D_crisis_backstop_governance — watch:** Public authorities may say no bailout ex ante, but stress can still route through banks, employment, insurer solvency, pension promises, or market-functioning tools. [S359] [S376]
- **20H_generational_intergovernmental_incidence — watch:** Retirement savers, policyholders, workers in portfolio companies, and future public capacity can absorb losses indirectly while sponsors and fee recipients keep earlier upside. [S359] [S376]

## Seniority waterfall under stress

1. **Senior lenders and private fund structures** — contractual seniority can protect credit investors ahead of workers, suppliers, and local communities. [S376]
2. **Fund sponsors, managers, and institutional investors** — private upside holders whose fees, carry, and valuation discretion should not be public-protected. [S376]
3. **Pension, insurance, retail-fund, and worker claimants** — indirect exposed claimants with less control over leverage, valuation, redemption gates, or portfolio-company restructuring. [S359] [S376]
4. **Banks and public stability agencies** — residual systemic channel if credit lines, correlated downgrades, fire sales, or employment shocks become macro-financial stress. [S359]

## Correction path

A passable case needs a nonbank stress map: fund leverage, liquidity terms, redemption gates, valuation governance, bank credit lines, insurer/pension/retail exposure, borrower concentration, employment exposure, resolution path, and public-liquidity no-bailout rules. Without that map, the cube should not treat the sector as purely private risk.

## Source anchors

[S359] [S376]

<!-- current_revision: rev0326; gate20_backstop_burndown: private_credit_active_evidence -->


## Rev0344 source-use burn-down note

Rev0344 binds formerly unused direct/context sources into this active case so the source ledger no longer carries high-value evidence outside the case/evidence/currentness lineage: [S49] [S33]. These bindings do not relax the verdict; they clarify which measurement, authority, or context burden the source supports.


## Rev0365 counterparty, redemption, and Form PF visibility migration

Rev0365 moves this case from a general nonbank warning into a concrete stress-perimeter map. The Federal Reserve May 2026 Financial Stability Report gives the size and retail-liquidity channel: private credit loans were about $1.4 trillion in the second half of 2025, about 10 percent of U.S. nonfinancial corporate debt and about one-third of below-investment-grade debt excluding bank loans; semi-liquid private-credit vehicles had about $425 billion in gross assets and $241 billion in net assets, with managers widely capping redemption requests at 5 percent of NAV as requests increased in late 2025 and early 2026. [S359]

The FSB May 2026 report keeps the global perimeter open: private credit is estimated at $1.5-$2 trillion, the ecosystem includes asset managers, insurers, pension funds and banks, retail access is increasing, and the sector at current size has not been tested in a severe downturn. [S376] This supports monitoring and stress-test obligations, but it does not prove a bailout or a current public loss.

OFR Brief 26-02 adds the missing counterparty-measurement route. It estimates two observable exposure channels: roughly $410-$540 billion in debt financing extended to private-credit funds and about $300 billion in limited-partner capital commitments. [S553] The same brief is also a constraint: fund identification remains manual, resource intensive, and imperfect, and the brief expressly does not represent official Treasury/OFR policy. [S553]

The Form PF surface cuts both ways. The 2024 amendments remain delayed until October 1, 2026, leaving a current data-timing blocker. [S555] The April 2026 SEC/CFTC proposal would raise the general Form PF threshold from $150 million to $1 billion, eliminating filing obligations for almost half of currently covered advisers by estimate, while still estimating coverage of over 90 percent of private-fund gross assets and adding a method to identify private-credit-active funds. [S554] Because Form PF is confidential and generally not public fund-level evidence, it cannot by itself answer claimant, worker, pensioner, policyholder, or public-upside questions. [S554]

The FSOC March 2026 readout confirms supervisory salience: Treasury staff briefed Council members on recent developments in private credit as part of the quarterly financial stability monitor and the Council voted to publish proposed nonbank-designation guidance. [S556] That is a monitoring edge, not a rescue-waterfall edge. Certification remains blocked until the cube has actual fund/vehicle exposure data, bank/insurer/pension concentration, redemption-gate records, valuation marks, borrower stress outcomes, and any public-liquidity facility terms with explicit haircuts, fees, recoveries, and public-upside recovery. [S359] [S376] [S553] [S554] [S555] [S556]
