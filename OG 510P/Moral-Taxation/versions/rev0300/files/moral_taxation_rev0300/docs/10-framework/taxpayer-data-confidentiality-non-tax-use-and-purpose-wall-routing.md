# Taxpayer data confidentiality, non-tax use, and purpose-wall routing

## Question in one sentence

When another agency, contractor, registry, court, or enforcement program seeks tax return information, what purpose wall prevents tax administration from becoming a non-tax surveillance or coercion channel?[S378][S545][S546]

## Companion routes

Use this route with:

- [`data-minimization-and-purpose-bounded-verification-routing.md`](data-minimization-and-purpose-bounded-verification-routing.md)
- [`beneficial-ownership-public-registry-and-privacy-burden-routing.md`](beneficial-ownership-public-registry-and-privacy-burden-routing.md)
- [`sanctions-aml-cft-de-risking-and-financial-access-routing.md`](sanctions-aml-cft-de-risking-and-financial-access-routing.md)
- [`../20-calibration/taxpayer-data-confidentiality-non-tax-use-and-purpose-wall-ladder.md`](../20-calibration/taxpayer-data-confidentiality-non-tax-use-and-purpose-wall-ladder.md)
- [`../../archive/228-taxpayer-data-confidentiality-disclosure-and-non-tax-use-rules-should-not-be-turned-into-surveillance-backdoors-or-purpose-drift-traps.md`](../../archive/228-taxpayer-data-confidentiality-disclosure-and-non-tax-use-rules-should-not-be-turned-into-surveillance-backdoors-or-purpose-drift-traps.md)

Route: tax data are collected under compulsion for tax administration. Any disclosure outside that purpose needs explicit authority, necessity, minimization, identity accuracy, logging, independent review, taxpayer remedy where lawful, and trust-impact review.[S378][S545]

## Core rule

The archive treats confidentiality as a fiscal-capacity rule, not only a privacy rule. People disclose income, addresses, family facts, immigration-adjacent records, and business relationships because the tax system promises bounded use. Purpose drift corrodes compliance and turns reporting into exposure.

## Routing table

| Signal | Start here | Default output |
|---|---|---|
| request is for tax administration | tax-use gate | share only what is necessary, logged, and authorized. |
| request is for non-tax law enforcement | statutory exception gate | require exact legal authority, court order where required, and identity-match control.[S378] |
| bulk data match is proposed | misidentification gate | sampling, error-rate test, no action on weak match, and independent approval. |
| immigrant, low-income, or safety-sensitive taxpayers may be chilled | trust gate | compliance-impact and protected-floor review.[S546][S547] |
| disclosure was unlawful or overbroad | repair gate | notice where lawful, suppression/use limits, damages/remedy path, and audit. |

## Anti-patterns

- **confidentiality backdoor** — tax records become an all-purpose enforcement database.
- **non-tax-use dragnet** — a broad public objective overrides the narrow collection purpose.
- **data-match policing** — weak identity matches produce coercive action.
- **trust liquidation** — short-term enforcement gain destroys long-term voluntary compliance.

## Source IDs only

[S378][S545][S546][S547]

[S378]: ../../SOURCES.md#S378
[S545]: ../../SOURCES.md#S545
[S546]: ../../SOURCES.md#S546
[S547]: ../../SOURCES.md#S547
