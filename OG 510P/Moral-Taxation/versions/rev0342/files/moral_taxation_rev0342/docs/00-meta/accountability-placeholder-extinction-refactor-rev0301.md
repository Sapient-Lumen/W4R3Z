# Accountability placeholder extinction and risk-family refactor — rev0301

## Why this pass mattered

Earlier revisions cleared placeholder accountability family by family. After rev0300, two clusters still used the literal beneficiary placeholder (`regulated_networks_platforms` and `release_integrity_currentness`), and three more families still passed audit while carrying generic symbolic beneficiaries and `benefit_or_rent_trace` evidence (`financial_system_risk`, `wealth_property_rent`, and `public_procurement_industrial_policy`). That was the remaining risk of a valid-looking but vague responsibility layer.

Rev0301 clears the problem archive-wide. No actor-accountability profile may now use `beneficiary_or_rent_recipient_to_trace`, `named_beneficiary_or_rent_recipient`, `rent_recipient_or_backstop_beneficiary`, or generic `benefit_or_rent_trace` evidence.

## Families specialized

- `regulated_networks_platforms`: spectrum/orbital commons, standards/accreditation gates, telecom universal-service/broadband surcharges, and digital advertising/speech transparency.
- `release_integrity_currentness`: route pruning, source hierarchy/current-law refresh, manifest/source-bijection regression, and case-contract answer regression.
- `financial_system_risk`: systemic backstops, crypto/stablecoin reporting, sanctions/AML de-risking, fiscal transparency, insurance/reinsurance protection gaps, event-contract gambling harms, creditor distress/surplus retention, and policyholder surplus.
- `wealth_property_rent`: land/location rent, dynastic transfers, public wealth/SOE/social dividend governance, annual wealth visibility/grouping/liquidity, site-rent netting/surplus, and real-value indexation/reset cadence.
- `public_procurement_industrial_policy`: procurement/subsidy/public upside, emergency relief speed/integrity/clawback, public-health stockpiles/allocation, publicly funded research/patents/open access/march-in, and defense/security procurement secrecy.

## Cube-axis refactor

Rev0301 also refactors cube records that were still too generic. The most important corrections are:

- release-integrity routes now expose archive governance, manifest/regression, source-currentness, route-retirement, and case-contract channels rather than `not_market_specific` / `not_channel_specific` defaults;
- financial routes now expose resolution funds, crypto custody, blocked-account channels, budget/tax-expenditure portals, creditor/insolvency rails, and policyholder surplus ledgers;
- wealth routes now expose site-value assessment, trusts/beneficial owners, public asset ledgers, wealth-register grouping, site-rent netting, and indexation reset channels;
- procurement routes now expose contract/subsidy conditions, emergency payment/clawback portals, stockpile allocation rails, research license/open-access rails, and classified procurement/audit channels.

## Regression rule

`tools/audit_actor_accountability_profiles.py` now contains a global ban on generic beneficiary markers and generic benefit-trace evidence. It also has family-specific checks for the five families specialized in this pass. This makes Rev0301 a checkpoint: future releases can add nuance, but they cannot silently return to placeholder responsibility.
