# Tax-benefit coordination, benefit cliffs, and effective marginal rate routing

## Question in one sentence

When taxes, credits, transfers, premiums, rent assistance, childcare, health benefits, and fees interact, how should the archive prevent hidden poverty traps and work penalties?[S81][S497][S572]

## Companion routes

Use this route with:

- [`decision-procedure.md`](decision-procedure.md)
- [`proceeds-routing-and-fiscal-reciprocity.md`](proceeds-routing-and-fiscal-reciprocity.md)
- [`incidence-and-protected-burden-routing.md`](incidence-and-protected-burden-routing.md)
- [`care-economy-second-earner-and-household-floor-routing.md`](care-economy-second-earner-and-household-floor-routing.md)
- [`../20-calibration/tax-benefit-coordination-cliff-smoothing-and-marginal-rate-ladder.md`](../20-calibration/tax-benefit-coordination-cliff-smoothing-and-marginal-rate-ladder.md)
- [`../../archive/235-tax-benefit-coordination-benefit-cliff-and-effective-marginal-rate-rules-should-not-be-turned-into-poverty-traps-or-work-penalties.md`](../../archive/235-tax-benefit-coordination-benefit-cliff-and-effective-marginal-rate-rules-should-not-be-turned-into-poverty-traps-or-work-penalties.md)

Route: The archive evaluates the combined tax-benefit schedule, not each program in isolation. A nominally generous credit, subsidy, or benefit becomes defective when phaseouts, recertification, premiums, fees, or work requirements create cliff losses or marginal rates that punish earnings, marriage, care, or formalization.[S81][S497][S572]

## Core rule

The archive evaluates the combined tax-benefit schedule, not each program in isolation. A nominally generous credit, subsidy, or benefit becomes defective when phaseouts, recertification, premiums, fees, or work requirements create cliff losses or marginal rates that punish earnings, marriage, care, or formalization.

## Routing table

| Signal | Start here | Default output |
|---|---|---|
| benefit ends abruptly at an income line | cliff gate | smooth phaseout, disregard, transitional protection, or automatic step-down. |
| multiple programs phase out together | stacked-EMTR gate | model combined marginal rate across taxes, transfers, fees, and premiums. |
| earnings increase triggers paperwork or recertification loss | administrative-cliff gate | use stable eligibility periods, ex parte renewal, and safe harbors. |
| marriage, care, disability, or childcare affects eligibility | household gate | test household structure and care cost before claiming work incentive. |
| program data sit in separate agencies | coordination gate | share only necessary data with purpose walls and correction rights. |

## Anti-patterns

- **poverty trap** — increased income leaves the household worse off.
- **work penalty** — earnings, hours, or formalization trigger stacked losses.
- **administrative cliff** — paperwork timing rather than income creates the loss.
- **program silo** — each agency claims fairness while the combined schedule fails.

## Source IDs only

[S81][S497][S572]

[S81]: ../../SOURCES.md#S81
[S497]: ../../SOURCES.md#S497
[S572]: ../../SOURCES.md#S572
