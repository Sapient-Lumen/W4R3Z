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

# Stablecoins, money-market funds, and Treasury liquidity backstop case — active Gate 20 case

## Verdict

**Correction required.** The case is no longer a generic “stablecoins may run” seed. It is a live law-and-rulemaking public-balance-sheet case. A cash-like private claim can be stabilized by public liquidity, payment-continuity policy, dealer/Treasury-market support, or deposit-insurance-adjacent rules even when issuer upside, platform fees, and reserve-management gains remain private. [S359] [S368] [S375] [S441] [S442] [S443] [S444] [S546] [S547] [S548] [S557] [S558] [S559] [S560] [S561] [S562] [S549] [S550] [S551] [S552]

## Current-law and rulemaking perimeter

The current evidence package now separates three things that rev0319 left too blended: market-growth risk, reserve/redemption law, and public backstop governance. The Federal Reserve stablecoin note records rapid 2025 growth, a $317 billion market capitalization as of April 2026, reserve-practice differences, complex intermediation chains, vertical integration, and retail/wallet adoption. That is not just crypto-market texture; it is a payment-continuity and Treasury-market interaction surface. [S375]

The GENIUS Act rulemaking pack creates real stabilizers but not a comfort verdict. The OCC, FDIC, FinCEN, and Treasury materials add reserve, redemption, capital, risk-management, custody/safekeeping, AML/CFT, sanctions, and state/federal oversight rails. Those rails reduce some run-risk ambiguity, but they do not yet settle the stress waterfall: who is haircut, who is made whole, who receives liquidity first, whether ordinary payment users outrank speculative holders, how reserve monetization affects Treasury-market liquidity, and what public upside recovery applies if public tools stabilize private issuers. [S441] [S442] [S443] [S444]



## Rev0364 reporting-data migration

Rev0364 converts the stablecoin blocker from “we need final rules and issuer data” into a concrete data-capture map. OCC Bulletin 2026-24 proposes a new information collection with a weekly confidential report for each payment stablecoin and a quarterly condition-and-income report for OCC-supervised permitted payment stablecoin issuers and foreign payment stablecoin issuers. [S549]

The PS-01 weekly instructions are especially important because they would collect standardized daily information on issuance, reserve assets, ownership concentration, trading activity, counterparties, secondary-market pricing, nonredeemable/restricted stablecoins, and redemption timing. [S550] That makes the Treasury/MMF/repo fire-sale pathway more auditable, but it also creates a confidentiality problem: the forms are supervisory data, not a guarantee of public, issuer-level disclosure. [S549] [S550]

The PS-02 quarterly instructions add income, balance-sheet, off-balance-sheet, capital, and operational-backstop information. [S551] This is the first concrete route for testing whether an issuer has capital and operational resources outside the reserve pool, but the proposed forms are still subject to change and do not themselves bind public-upside recovery or failure-waterfall terms. [S549] [S551]

The FDIC proposed rule adds a parallel stress boundary for FDIC-supervised PPSIs: proposed two-business-day redemption, custody/safekeeping requirements, identifiable reserves, capital/risk-management standards, and proposed no pass-through deposit-insurance treatment for reserve deposits. [S552] These are material protections and material qualifiers. They do not certify the case because final rules, issuer records, actual supervisory filings, insolvency priority, public-liquidity terms, and public-upside recovery remain missing. [S546] [S549] [S550] [S551] [S552]

## Rev0363 statutory/current-law migration

Rev0363 converts the highest-risk legal perimeter into locator-bound claim edges rather than comfort language. Public Law 119-27 now supplies the primary law-text anchor: payment stablecoin issuers must maintain identifiable reserves at least 1:1, the law expressly disclaims U.S. full-faith-and-credit/government and deposit/share-insurance backing, and issuers may not pay interest or yield solely for holding, use, or retention of a payment stablecoin. [S546]

That improves the case, but it does not certify it. The Federal Reserve market note still makes the scale material, with stablecoin market capitalization recorded at $317 billion as of April 6, 2026. [S375] The Federal Reserve cross-border note frames payment stablecoins as payment/monetary-policy infrastructure under the GENIUS Act framework, while Treasury/FinCEN rulemaking adds AML/CFT, sanctions, and technical-control obligations. [S547] [S548] [S443]

The decisive blocker is no longer whether a statute exists; it is whether final rules, issuer disclosures, custody and insolvency terms, redemption timing, reserve monetization, public liquidity terms, and public-upside recovery allocate stress losses in a way the cube can certify. [S441] [S442] [S443] [S444] [S546]


## Rev0366 Treasury basis, repo, and clearing-plumbing migration

Rev0366 splits the Treasury-liquidity part of this case away from stablecoin-only analysis. The public-balance-sheet risk is not just that a stablecoin reserve pool might sell Treasury bills; it is that several private cash-like or leveraged balance sheets can all lean on the same Treasury/repo/MMF plumbing and then expect public market-functioning support without a public-upside claim. [S359] [S557] [S558]

The Federal Reserve May 2026 Financial Stability Report makes the risk current: hedge fund leverage remained near record highs in the comprehensive Form PF series, and the report names basis trade as a salient risk cited by survey respondents. [S359] The report also states the boundary that matters for certification: high leverage can spill over if a fund suddenly loses access to funding, but that observation does not itself identify the rescue waterfall, claimant priority, or public recovery terms. [S359]

Dallas Fed research adds the mechanism. Leveraged cash-futures basis and swap-spread trades are net-funding-demand trades: hedge funds finance long cash Treasury positions in repo while carrying short derivatives positions. The article estimates hedge fund net repo borrowing at roughly $1.8 trillion by year-end 2025, over twice the level at the start of 2024, and explains that this demand pressures secured funding rates because dealers transmit the borrowing demand to money-market funds and other cash providers. [S557] This supports a Treasury-market-plumbing risk perimeter; it does not prove that public support will absorb private losses. [S557]

The Federal Reserve cross-border note adds a measurement failure that matters to the cube. It estimates Cayman-domiciled hedge fund Treasury holdings reached $1.85 trillion by end-2024, says TIC data do not capture the activity well, and shows that the resulting measurement gap affects Financial Accounts estimates of household Treasury holdings, saving, and net worth. [S558] That is a direct warning against using national-account surfaces as if the basis-trade exposure were cleanly visible. [S558]

Treasury clearing is therefore a live instrument, not a completed remedy. The SEC implementation hub lists the extended compliance dates as December 31, 2026 for eligible cash-market transactions and June 30, 2027 for eligible repo-market transactions. [S559] The April 2026 SEC implementation statement says material work remains on exemptive relief, extraterritorial scope, outages/failed trades, customer protection, cross-margining, and liquidity/competition effects. [S562] Central clearing may improve margin, netting, and counterparty-risk visibility, but rev0366 treats it as a currentness blocker until actual implementation, margin economics, default-management terms, and public-upside recovery are bound. [S559] [S562]

The acceptance test is now explicit: a certifiable Treasury-liquidity backstop case needs live proxies for leveraged-fund Treasury futures shorts and Form PF Treasury exposures, clearing implementation status, repo funding stress, margin calls, dealer/MMF/cash-provider incidence, and any Federal Reserve/Treasury/clearing-agency/public market-functioning support terms. OFR’s Hedge Fund Monitor supplies two public proxy routes for this sprint, but those proxies remain aggregate and confidentiality-limited. [S560] [S561]

## Gate 20 subgate findings

- **20C_contingent_liabilities_guarantees — watch:** Private cash-like claims should be mapped as contingent public-stability liabilities, especially when reserves are concentrated in Treasury bills, repo, bank deposits, or other short-term instruments. [S359] [S368] [S375] [S441] [S442]
- **20D_crisis_backstop_governance — blocked:** The case still lacks a final priority, haircut, facility, and sunset map for issuer failure, wallet/custody failure, reserve-fire-sale stress, or payment-continuity intervention. [S441] [S442] [S444]
- **20E_public_upside_recovery — missing:** Public upside recovery is still not defined for a scenario where public liquidity, market-functioning support, or regulatory forbearance stabilizes private issuers or platforms. [S359] [S368] [S441] [S442]
- **20F_central_bank_quasi_fiscal_visibility — watch:** Treasury-market and central-bank market-functioning tools can become quasi-fiscal support surfaces even where no explicit issuer bailout is announced. [S359] [S368] [S375]

## Seniority waterfall under stress

1. **Ordinary payment continuity and legal redemption** — legitimate public-interest priority only if issuer equity, sponsor carry, and platform rents are not protected by default. [S441] [S442]
2. **Stablecoin holders' reserve-backed claims** — claims depend on legal segregation, valuation, custody, redemption timing, and insolvency treatment. [S441] [S442]
3. **Issuers, wallets, custodians, dealers, and infrastructure providers** — should absorb private first-loss and operational-risk costs before public liquidity is used. [S375] [S441] [S442] [S443]
4. **Public liquidity, Treasury-market functioning, and future public capacity** — residual support surface if reserve liquidation, payment disruption, or short-term funding stress threatens broader markets. [S359] [S368] [S375]

## Correction path

A passable case now needs a dated stablecoin backstop term sheet: issuer class, reserve composition, custody/segregation, redemption right, insolvency priority, AML/sanctions operating capability, state/federal supervisor, stress-test assumption, fire-sale channel, ordinary payment-user protection, and public-upside recovery if public downside is used.

## Evidence debt

- final GENIUS Act implementing rules and comment-period changes
- reserve monetization under simultaneous redemption and Treasury-market stress
- issuer/wallet/custodian failure waterfall and bankruptcy remoteness
- ordinary payment-user protection versus speculative token-holder protection
- fee, penalty-rate, clawback, or equity-like public recovery if public tools stabilize private issuers

## Source anchors

[S359] [S368] [S375] [S441] [S442] [S443] [S444] [S546] [S547] [S548] [S557] [S558] [S559] [S560] [S561] [S562]

<!-- current_revision: rev0367; gate20_backstop_burndown: stablecoin_rulemaking_currentness; stablecoin_law_waterfall_refactor: active -->
