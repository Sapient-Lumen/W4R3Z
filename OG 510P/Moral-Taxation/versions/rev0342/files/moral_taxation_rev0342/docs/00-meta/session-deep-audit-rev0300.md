# Session deep audit — rev0300

## Priority chosen

The rev0300 priority was `cross_border_reporting`, because after rev0299 it was the largest remaining route family with both beneficiary placeholders and generic benefit-trace evidence. It also carries high moral risk: cross-border routes can turn foreignness, remitter status, claimant status, migrant status, or source-state weakness into a burden assignment while the real controlling actor sits in a treaty, customs, registry, KYC, portal, exchange, or MAP channel.

## Substantive change

All 6 cross-border-reporting profiles were rewritten. The family now routes responsibility through concrete control points: inclusive coordination tables, customs/CBAM registries, remittance corridors, immigration fee/waiver gates, withholding/reclaim chains, competent-authority/MAP queues, central GIR exchange, and claim-split/apportionment formulas.

## Cube refactor

The pass also corrected cross-border cube-axis defaults. Generic `not_market_specific`, `not_channel_specific`, `legal_risk_transfer`, `not_remedy_specific`, and `classification_integrity` values were replaced or supplemented with route-specific market, channel, burden, rights, remedy, and moral-operation values. The most important repairs were to `international_coordination_claim_split` and `un_inclusive_international_tax`.

## Quantitative result

- Cross-border beneficiary placeholders: 6 -> 0.
- Cross-border generic benefit-trace bundles: 6 -> 0.
- Archive-wide beneficiary placeholders remaining: 8.
- Archive-wide generic benefit-trace bundles remaining: 27.
- Primary-accountable actor categories: 133.

## Remaining risk

The remaining placeholder clusters are now small: `regulated_networks_platforms` and `release_integrity_currentness`. There are also generic-evidence-only clusters in `financial_system_risk`, `wealth_property_rent`, and `public_procurement_industrial_policy`. The next best pass should probably clear the two remaining placeholder clusters together, then return to generic evidence in financial/wealth/procurement routes.
