# Consolidated audit report — rev0321

Active revision: rev0321. Codename: `answer-packet-obligation-audit-refactor`. Generated: 2026-06-18T10:49:00Z.

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

## Answer-packet runtime audit

Answer runtime status: profile_backed_answer_packet_emitted
Answer packets: 122
Answer route limit: 5
Answer facts-only candidate limit: 8
Answer route-limit recall: 166/166
Answer candidate misses: 0
Must-not-answer recall: 241/241
Blocked-shortcut recall: 1220/1220
Profile-obligation recall: 1830/1830
Source-obligation recall: 7663/7663
Currentness-obligation recall: 295/295
Complete answer-step packets: 122/122
Contract-free answer-emitter cases: 122/122
Complete source packets: 122/122
Complete profile packets: 122/122

The answer emitter still does not decide final law, precedence, or estimates. The improvement is narrower and more important for this revision: the emitted answer packet can no longer be only a list of route IDs. It must surface the live remedy default move, blocked move, guardrails, policy-action category error, accountable actor, source packet, currentness claims, review triggers, unknowns, and must-not-answer warnings for every selected route.

## Profile audits

Remedy profiles: 155
Policy-action profiles: 155
Actor-accountability profiles: 155
Repository-process placeholders in remedy escalation triggers: 0
Repository-process placeholders in policy-action escalation triggers: 0

## Axis and waste audits

Declared axis values still equal live route usage plus active case-contract requirements. Rev0321 does not enlarge doctrine vocabulary; it makes runtime answer emission carry live profile obligations.

No negative bytes-saved metrics remain.

## Refactor note

`tools/answer_case.py` now loads cube, source, remedy, policy-action, accountability, and prepared route state once per invocation rather than rebuilding those surfaces for every case. The new audit is a runtime obligation audit, not a new policy registry.

## Current limitation

This is now a candidate router plus a checked profile-backed answer packet. It still is not a final answer engine: precedence resolution, jurisdiction-specific current-law validation, complete citations, quantitative fiscal estimates, and human conflict resolution remain outside this runtime layer.
