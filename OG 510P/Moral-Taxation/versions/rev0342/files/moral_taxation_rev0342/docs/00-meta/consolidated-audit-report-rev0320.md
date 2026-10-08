# Consolidated audit report — rev0320

Active revision: rev0320. Codename: `facts-runtime-full-route-coverage-refactor`. Generated: 2026-06-18T10:18:00Z.

## Runtime case-contract audit

Case contracts: 122
Golden cases: 122
Route coverage: 155/155 (100.0%)
Coverage floor: 155
Runtime status: facts_and_axes_candidate_router_invoked
Runtime candidate limit: 5
Runtime top-5 route recall: 166/166
Facts-only candidate limit: 8
Facts-only top-8 route recall: 166/166
Runtime top-N exact cases: 115/122
Runtime primary matches: 121/122
Facts-only primary matches: 104/122
Runtime candidate misses: 0
Facts-only candidate misses: 0
Case-only axis values: 229

Family coverage:
- `controller_ai`: 21/21
- `cross_border_reporting`: 6/6
- `environment_climate_commons`: 10/10
- `financial_system_risk`: 8/8
- `labor_care_benefits`: 11/11
- `legal_enforcement_penalty`: 11/11
- `public_finance_core`: 44/44
- `public_procurement_industrial_policy`: 5/5
- `regulated_networks_platforms`: 4/4
- `release_integrity_currentness`: 4/4
- `social_floor_public_services`: 8/8
- `tax_administration_access`: 17/17
- `wealth_property_rent`: 6/6

Case-only axis values by axis:
- `anti_pattern`: 41
- `base`: 83
- `instrument`: 16
- `proof_posture`: 51
- `review_trigger`: 38


## Profile audits

Remedy profiles: 155
Policy-action profiles: 155
Actor-accountability profiles: 155
Repository-process placeholders in remedy escalation triggers: 0
Repository-process placeholders in policy-action escalation triggers: 0

## Axis and waste audits

Declared axis values still equal live route usage plus active case-contract requirements. Rev0320 does not enlarge the doctrine vocabulary; it converts the remaining uncovered route records into checked scenario obligations.

No negative bytes-saved metrics remain.

## Answer skeleton

`tools/answer_case.py` emits a first deterministic answer skeleton from candidate routes, remedy profiles, policy-action profiles, and actor-accountability profiles. It returns accountable actors, default moves, blocked moves, guardrails, source IDs, unknowns, and must-not-answer warnings without reading answer contracts.

## Current limitation

This is now a two-mode candidate-router runtime plus an answer-skeleton emitter, not yet a full answer engine. It proves that every current route has an active case and that expected routes are recoverable both by combined normalized facts plus axes and by written facts alone. It does not yet emit final precedence decisions, complete citations, quantitative estimates, or jurisdiction-specific current-law answers.
