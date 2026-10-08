# Telecom universal-service, broadband-affordability, and surcharge ladder

## Question in one sentence

When universal-service funding is collected through telecom bills or carriers, how should the base, surcharge visibility, and low-income connectivity floor be calibrated so the access floor is not financed by the people least able to pay?[S632][S633][S647][S653]

## Companion routes

Use this memo with:

- [`../10-framework/telecom-universal-service-broadband-affordability-and-surcharge-routing.md`](../10-framework/telecom-universal-service-broadband-affordability-and-surcharge-routing.md)
- [`incidence-and-protected-burden-routing.md`](../10-framework/incidence-and-protected-burden-routing.md)
- [`user-fee-service-charge-utility-and-public-access-toll-routing.md`](../10-framework/user-fee-service-charge-utility-and-public-access-toll-routing.md)

## Option scan

| Option | Shape | Archive verdict |
|---|---|---|
| A — legacy interstate-revenue factor | fund support through a percentage factor on a shrinking telecom contribution base | Administratively familiar but unstable when factor spikes and carriers pass through line items. |
| B — broadened communications base | spread support over broadband, voice, platform, or connectivity revenues | Stronger if legal authority, incidence, and low-income protection are explicit. |
| C — appropriated public funding | fund universal service through the ordinary budget | Most transparent, but must protect program durability and avoid annual political cliff. |
| D — targeted affordability credit | direct benefit or bill credit for eligible low-income, rural, tribal, or disabled users | Required when bill-side charges threaten the very connectivity floor the program claims. |
| E — provider support with service conditions | subsidy goes to carriers for high-cost or low-income service | Accept only with buildout, price, quality, clawback, and audit conditions. |

## Parameter ladder

1. **contribution-base test** — Measure whether the base is shrinking, volatile, or mismatched to modern connectivity markets.
2. **line-item visibility and markup ban** — Permit truthful disclosure, but bar carrier markup or misleading surcharge labels beyond authorized recovery.
3. **low-income incidence screen** — Model the full bill impact for Lifeline/ACP-like households, prepaid users, rural households, and tribal communities.
4. **support-condition audit** — Tie provider support to speed, reliability, coverage, price, and service-quality obligations.
5. **affordability credit adequacy** — Set credits against actual essential service cost, not symbolic amounts that leave disconnection risk.
6. **public-capacity option** — Ask whether direct public funding or municipal/tribal capacity would reduce dependence on carrier pass-through.
7. **delegation/current-law status** — Mark nondelegation/litigation posture and agency authority rather than treating the surcharge as timeless.
8. **quarterly factor trigger** — Require review when factor exceeds a threshold, changes rapidly, or base erosion accelerates.
9. **anti-supplantation** — Support should add connectivity, not replace carrier baseline duties or state/local commitments.
10. **review trigger** — Reopen after contribution-factor spike, court ruling, program expiration, disconnection rise, or service audit failure.

## Default settings

| Parameter | Default | Redesign trigger |
|---|---|---|
| Contribution base | Broad, stable, visible, and floor-tested | Narrow shrinking base with high quarterly factor. |
| Bill recovery | Authorized recovery only, no markup, truthful line item | Provider-created surcharge above obligation or hidden spread. |
| Affordability protection | Direct low-income/tribal/rural credit and no-disconnect guard | Users pay a surcharge that funds benefits they cannot access. |
| Provider support | Conditioned and clawbackable | Subsidy without service quality or buildout proof. |
| Review cadence | Quarterly factor review plus annual adequacy audit | No review despite factor spikes or connectivity loss. |

## Anti-pattern definitions

- **line item rent** — carriers turn a public contribution into a marked-up or misleading bill charge.
- **low income cross subsidy** — low-income users fund their own connectivity floor through unavoidable bill surcharges.
- **legacy base spiral** — a shrinking revenue base drives a higher factor, producing more avoidance and political instability.
- **provider support without service** — funds flow to carriers without enforceable coverage, price, quality, or clawback conditions.
- **hidden connectivity tax** — a compulsory bill charge functions like taxation without budget visibility, floor review, or current-law status labels.

## Accountability capsule

Authoritative assignment: route `telecom_universal_service_broadband_affordability_surcharge` in [`actor-accountability-profiles.json`](../00-meta/actor-accountability-profiles.json).

- Duty owner: `universal_service_administrator_carrier_provider_or_billing_entity_with_contribution_line_item_and_affordability_control`.
- Rent/benefit trace: `telecom_carrier_broadband_provider_legacy_service_provider_or_billing_intermediary_capturing_line_item_markup_support_flow_or_base_spiral_rent`.
- Bottleneck/evidence: `universal_service_contribution_factor_and_assessment_rail; carrier_billing_line_item_channel +2 more`; evidence starts with `contribution_factor_assessment_base_and_provider_remittance_record; customer_bill_line_item_markup_and_fee_disclosure_sample +4 more`.
- Fallback duty: `public_body_must_preserve_fallback_connectivity_affordability_credit_lifeline_tribal_and_rural_service_path_with_no_forfeiture_from_provider_or_billing_failure`.


## Source IDs only

[S632][S633][S647][S653]

[S632]: ../../SOURCES.md#S632
[S633]: ../../SOURCES.md#S633
[S647]: ../../SOURCES.md#S647
[S653]: ../../SOURCES.md#S653
