# Legal-enforcement accountability refactor — rev0296

## Why this was the riskiest next slice

After rev0295, the largest remaining placeholder families were `labor_care_benefits` and `legal_enforcement_penalty` at eleven profiles each. I chose legal enforcement first because generic responsibility language is most dangerous where the state can seize property, impose penalties, compel records, threaten criminal referral, extend supervision, expose privileged material, or attach personal liability.

The pre-refactor family had two separate defects:

1. all 11 legal-enforcement profiles still used `beneficiary_or_rent_recipient_to_trace` and generic `benefit_or_rent_trace` evidence; and
2. seven route records had real route documents but cube axes inherited from a generic administrative-penalty template, which made criminal referral, summons, wrongful levy, trust-fund recovery, whistleblower-tip, penalty-safe-harbor, and hidden-tax visibility routes look interchangeable.

## Route-family refactor

Rev0296 rewrites the full `legal_enforcement_penalty` actor-accountability family. Each route now names the coercive actor, the beneficiary or rent recipient, the bottleneck / record channel, the protected burden bearer, the non-responsible actor, the default liability or remedy move, the public fallback duty, and a route-specific evidence packet.

The refactor covers:

- community supervision, private probation, monitoring, and reentry fees;
- civil asset forfeiture, equitable sharing, and owner remedy;
- whistleblower / relator reward and public-funds recovery;
- cybersecurity breach resilience and incident-cost allocation;
- burden salience, disclosure, and hidden-tax visibility;
- criminal tax referral, voluntary disclosure, restitution, and civil reentry;
- culpability-scaled penalties, safe harbors, abatement, and criminal side screens;
- summons, third-party contact, John Doe demands, and privilege;
- transferee, nominee, alter-ego, successor, and wrongful-levy theories;
- trust-fund recovery responsible-person and willfulness; and
- whistleblower-tip classification, confidentiality, award, and accused-taxpayer protection.

## Core correction

The legal-enforcement family now uses a coercion-first responsibility rule:

> The accountable actor is not whoever is nearest the file, invoice, device, account, source, property, title, or payment rail. It is the actor that controlled coercive power, duty, evidence access, property custody, notice, contestability, proceeds, willfulness/fault findings, or the public fallback channel.

That rule blocks several recurring errors:

- treating probationers or family payers as responsible for private-probation rent;
- treating property possession or owner default as forfeiture responsibility;
- treating a whistleblower tip as taxpayer proof;
- treating a breach victim or ordinary user as responsible for a controller's security failure;
- treating low salience as a substitute for democratic disclosure;
- treating tax due, audit frustration, or voluntary disclosure as criminal proof;
- treating error amount as culpability;
- treating third-party record custody as waiver of privilege or notice;
- treating family proximity or shared address as nominee liability;
- treating officer title, check access, or bookkeeping as trust-fund willfulness; and
- treating confidential source status or award size as merits evidence.

## Cube-axis refactor

Rev0296 also updates the generic cube axes for seven route records that had been over-normalized to `administrative_penalty`, `penalty`, `protected_floor`, `liability_by_default`, and `new_calibration_file`. The records now expose the actual route distinctions: criminal referral, voluntary disclosure, restitution credit, summons / John Doe demand, privilege / taint review, nominee / transferee property, wrongful levy, trust-fund recovery, hidden-tax disclosure, and whistleblower ghost-proof risk.

This is intentionally a bounded cube refactor, not a new registry. The objective was to make existing route records less misleading, not to add another abstraction layer.

## Remaining debt

Rev0296 leaves five main placeholder clusters: `labor_care_benefits`, `environment_climate_commons`, `social_floor_public_services`, `cross_border_reporting`, and small regulated-network / release-integrity families. The next substantive pass should probably take `environment_climate_commons` if the goal is non-compensable harm and public-trust accounting, or `labor_care_benefits` if the goal is household, employer, and platform burden assignment.
