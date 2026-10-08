---
status: active_bridge
claim_kind: program_protocol
route_role: score_mediated_exclusion_core
canonical_anchor: false
route_refs:
- score_mediated_exclusion_core
- case_calibration_core
supersedes: null
depends_on:
- verdict-engine-and-certification-gates.md
- scoreboard-schema.json
source_refresh_due: 2026-12-31
case_pressure: rev0315_score_mediated_exclusion
---


# Insurance scoring and surveillance-pricing guardrails

Use this guardrail when a household needs insurance, a quote, a utility-like subscription, a travel/mobility product, or another essential product whose price is data-personalized.[S290][S291][S292][S293][S294]

## Guardrail questions

- What data are used: credit, claims, location, driving, browsing, device, health-adjacent, shopping, demographic, or inferred vulnerability?
- Is the price or eligibility decision individualized, group-based, or both?
- Are variables predictive, legally permissible, and non-proxying protected or poverty status?
- Can a consumer see and contest the causal factor?
- Can the regulator examine vendor data, model code, documentation, and disparate impact?
- Does the product protect wealth or become unaffordable exactly for households exposed to loss?

## Required rails

- adverse-action notices with meaningful factor specificity;
- state/regulator model examination authority;
- external-consumer-data inventory;
- disparate-impact and proxy testing;
- ban or limit weakly predictive credit/location/behavioral variables for essential coverage;
- affordability backstop for mandatory or practically necessary insurance;
- surveillance-pricing disclosure and data-minimization rules;
- public monitoring of price spread by income, race, disability, geography, and claim history.

## Verdict consequence

Insurance cannot be counted as a private buffer when risk scoring or personalized pricing makes coverage unavailable or unaffordable for the same households most likely to face loss.
