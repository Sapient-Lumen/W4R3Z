# Digital-asset basis, custody, stablecoin, and reporting ladder

## Question in one sentence

What ladder should allocate digital-asset tax reporting, basis protection, stablecoin risk pricing, and taxpayer correction rights without turning new reporting rails into penalty machines?[S487][S488][S489][S490]

## Companion routes

Use this memo with:

- [`../10-framework/digital-asset-crypto-stablecoin-and-broker-reporting-routing.md`](../10-framework/digital-asset-crypto-stablecoin-and-broker-reporting-routing.md)
- [`../10-framework/third-party-reporting-correction-and-bounded-recipient-shelter-routing.md`](../10-framework/third-party-reporting-correction-and-bounded-recipient-shelter-routing.md)
- [`../10-framework/financial-systemic-risk-guarantee-and-liquidity-backstop-routing.md`](../10-framework/financial-systemic-risk-guarantee-and-liquidity-backstop-routing.md)
- [`third-party-reporting-correction-and-bounded-recipient-shelter-ladder.md`](third-party-reporting-correction-and-bounded-recipient-shelter-ladder.md)

## Option scan

| Option | Shape | Archive verdict |
|---|---|---|
| A — no special reporting | self-report all digital-asset facts. | Insufficient for custodial brokers with clear records. |
| B — custodial broker reporting | report proceeds and basis where records exist. | Default with correction and transition relief. |
| C — broad facilitator reporting | treat interfaces and software as brokers. | Reject unless record/control capacity is real. |
| D — stablecoin reserve/risk regime | reserve, redemption, run-risk, and issuer-income rules. | Add where stablecoin resembles payment/deposit instrument. |
| E — chain-analytics enforcement | infer ownership and taxable events from traces. | Use only as lead, not final proof, with notice and contest. |

## Ten-gate ladder

1. **asset gate** — classify digital asset, stablecoin, NFT, tokenized security, wrapped asset, reward, fork/airdrop, or payment token without assuming tax treatment from label.
2. **realization gate** — separate sale/exchange/payment/reward from self-transfer, bridge, custody move, wallet migration, or internal record change.
3. **custody gate** — identify who has customer identity, order execution, proceeds, basis, transfer-in records, wallet control, and practical reporting power.[S487]
4. **basis gate** — protect lot identification, wallet-by-wallet basis, transfer statements, missing-basis flags, and taxpayer correction before penalty.[S488]
5. **transition gate** — apply transitional relief where rules, systems, withholding, or basis methods are changing.[S489]
6. **stablecoin gate** — test redemption promise, reserve yield, seigniorage/spread, run risk, payment-system role, and implicit public backstop.[S490]
7. **privacy gate** — collect tax-relevant facts without indiscriminate wallet surveillance or sensitive network mapping.
8. **mismatch gate** — when third-party reports conflict with taxpayer records, use bounded shelter and issue-scoped correction.
9. **cross-border gate** — coordinate CARF/CRS-style data with notice, data minimization, and correction rights.
10. **review gate** — revisit after reporting-system errors, market shocks, stablecoin runs, broker failures, or high mismatch rates.

## Default settings

| Posture | Instrument | Guardrail |
|---|---|---|
| custodial sale | broker report | basis/correction path and transition relief. |
| self-custody transfer | no realization by transfer alone | preserve basis record. |
| DeFi/no custody/no records | no broad broker duty by interface alone | use targeted summons/reporting where control exists. |
| stablecoin issuer spread/run risk | ordinary tax plus reserve/risk rule | avoid shadow public backstop. |
| gross proceeds without basis | bounded mismatch shelter | no automatic gain assumption. |

## Failure-mode capsule

Axes: `screening_or_custody_lockout`, `reserve_or_surplus_retention`, `trapdoor_or_cliff`.

## Recalibration trigger capsule

Triggers: `broker_basis_gap`, `stablecoin_reserve_break`, `custody_freeze_spike`.


## Accountability capsule

Authoritative assignment: route `digital_asset_crypto_reporting_stablecoin` in [`actor-accountability-profiles.json`](../00-meta/actor-accountability-profiles.json).

- Duty owner: `crypto_platform_custodian_stablecoin_issuer_or_reporting_broker_with_basis_custody_reserve_and_wallet_control`.
- Rent/benefit trace: `exchange_broker_custodian_stablecoin_issuer_market_maker_or_chain_analytics_vendor_capturing_float_spread_listing_reserve_or_reporting_rent`.
- Bottleneck/evidence: `exchange_and_broker_reporting_rail; wallet_custody_and_key_control_record +3 more`; evidence starts with `broker_information_return_gross_proceeds_and_basis_record; wallet_transfer_key_control_freeze_and_custody_record +4 more`.
- Fallback duty: `public_body_must_preserve_fallback_small_user_basis_safe_harbor_wallet_correction_redemption_window_and_no_forfeiture_when platform records fail`.


## Source IDs only

[S487][S488][S489][S490]

[S487]: ../../SOURCES.md#S487
[S488]: ../../SOURCES.md#S488
[S489]: ../../SOURCES.md#S489
[S490]: ../../SOURCES.md#S490
