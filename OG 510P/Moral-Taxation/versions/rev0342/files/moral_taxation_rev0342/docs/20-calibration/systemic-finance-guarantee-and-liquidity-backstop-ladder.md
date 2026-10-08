# Systemic-finance guarantee and liquidity-backstop ladder

## Question in one sentence

What is the smallest workable ladder for choosing between ordinary taxation, insurance premiums, resolution-fund contributions, systemic-risk surcharges, leverage/liquidity charges, transaction taxes, support-conditioned clawbacks, or non-tax regulation for financial-sector public-backstop cases?[S453][S454][S455]

## Companion routes

Use this memo with:

- [`../10-framework/financial-systemic-risk-guarantee-and-liquidity-backstop-routing.md`](../10-framework/financial-systemic-risk-guarantee-and-liquidity-backstop-routing.md)
- [`../10-framework/failure-ordering-and-limited-liability-routing.md`](../10-framework/failure-ordering-and-limited-liability-routing.md)
- [`../10-framework/creditor-bondholder-and-debt-service-pass-through-routing.md`](../10-framework/creditor-bondholder-and-debt-service-pass-through-routing.md)
- [`../10-framework/insurance-premium-and-risk-pool-pass-through-routing.md`](../10-framework/insurance-premium-and-risk-pool-pass-through-routing.md)
- [`../10-framework/net-fiscal-stack-and-hidden-negative-tax-routing.md`](../10-framework/net-fiscal-stack-and-hidden-negative-tax-routing.md)
- [`proceeds-visibility-local-share-and-earmarking-ladder.md`](proceeds-visibility-local-share-and-earmarking-ladder.md)

## Option scan

| Option | Shape | Archive verdict |
|---|---|---|
| A — ordinary tax only | tax profits and compensation as usual. | Correct when no special public backstop or systemic externality is present. |
| B — broad FTT | tax transactions or trades. | Use only after market-function and incidence review; often too blunt. |
| C — risk/guarantee contribution | price insured liabilities, runnable funding, systemic footprint, and backstop value. | Adopt as default. |
| D — crisis-support clawback | recover public rescue value from later surplus, dividends, buybacks, or creditor gains. | Adopt when support was used or credibly priced in. |
| E — non-tax prudential rule | capital, liquidity, margin, activity restriction, or resolution planning. | Prefer when taxation would simply sell permission for unsafe risk. |

## Ten-gate ladder

1. **perimeter gate** — identify bank, insurer, broker-dealer, exchange, clearinghouse, payment rail, money fund, private-credit fund, stable-value issuer, or other runnable-liability actor.
2. **public-backstop gate** — list explicit guarantees, deposit insurance, central-bank facilities, emergency liquidity, resolution authority, public guarantees, and credible implicit support.
3. **systemic-footprint gate** — measure size, interconnectedness, substitutability, complexity, cross-jurisdiction activity, and critical payment/credit functions.[S453]
4. **runnable-liability gate** — map deposits, repos, commercial paper, margin chains, redemption promises, stable-value instruments, and liquidity mismatch.
5. **loss-waterfall gate** — identify who bears first loss: equity, management, subordinated debt, senior creditors, deposit-insurance fund, central bank, treasury, households, SMEs, or municipalities.
6. **support-history gate** — record crisis support, forbearance, asset guarantees, special facilities, or emergency rules, including whether support was repaid at market risk price.[S455]
7. **instrument-selection gate** — choose ordinary tax, risk premium, levy, surcharge, reserve, bond, transaction tax, clawback, or non-tax prudential rule.[S454]
8. **incidence gate** — test pass-through to small depositors, borrowers, pension savers, municipalities, SMEs, and protected households before adopting the rate.
9. **proceeds gate** — route proceeds first to resolution funds, deposit-insurance repair, public backstop repair, or continuity of household/SME payment and credit services.
10. **review gate** — revisit after designation changes, crisis support, rapid asset growth, new runnable products, perimeter migration, or nonbank leverage shocks.

## Default settings

| Posture | Instrument | Proceeds rule |
|---|---|---|
| ordinary finance, no special backstop | ordinary tax stack | general fund. |
| insured/runnable liabilities | risk-based premium or liquidity charge | insurance/resolution fund first. |
| systemic designation or implicit support | systemic-risk surcharge or capital/reserve requirement | public backstop repair. |
| crisis aid or guarantee used | clawback, support fee, compensation/buyback restraint | taxpayer/recovery fund first. |
| unsafe non-compensable risk | prohibition, capital/liquidity rule, or resolution condition | do not sell permission through tax alone. |

## Failure-mode capsule

Axes: `backstop_arbitrage`, `reserve_or_surplus_retention`, `liability_misassignment`.

## Recalibration trigger capsule

Triggers: `public_backstop_used`, `resolution_fund_shortfall`, `executive_payout_before_recovery`.


## Accountability capsule

Authoritative assignment: route `systemic_finance_backstop` in [`actor-accountability-profiles.json`](../00-meta/actor-accountability-profiles.json).

- Duty owner: `systemic_financial_institution_resolution_authority_or_guarantee_sponsor_with_risk_origin_backstop_and_clawback_control`.
- Rent/benefit trace: `systemic_firm_creditor_shareholder_executive_or_funding_market_capturing_public_guarantee_liquidity_or_too_big_to_fail_option_value`.
- Bottleneck/evidence: `resolution_fund_and_deposit_insurance_assessment_rail; liquidity_facility_and_guarantee_authorization_record +2 more`; evidence starts with `balance_sheet_leverage_liquidity_and_interconnected_exposure_record; guarantee_liquidity_facility_and_resolution_authorization_file +4 more`.
- Fallback duty: `public_body_must_preserve_fallback_depositor_access_payment_continuity_resolution_fund_and_taxpayer_repair_when systemic backstop is invoked`.


## Source IDs only

[S453][S454][S455]

[S453]: ../../SOURCES.md#S453
[S454]: ../../SOURCES.md#S454
[S455]: ../../SOURCES.md#S455
