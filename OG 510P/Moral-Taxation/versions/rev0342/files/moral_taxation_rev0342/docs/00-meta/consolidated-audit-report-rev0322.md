# Consolidated audit report — rev0322

Active revision: rev0322. Codename: `claim-provenance-profile-index-refactor`. Generated: 2026-06-18T11:22:00Z.

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

## Runtime profile-index audit

Route profile index entries: 155
Route profile index drift: 0

The answer emitter now consumes a generated runtime index that joins route, remedy, policy-action, and actor-accountability profiles once at build time. The source surfaces remain authoritative: the index stores input hashes, mirrors every live route, and fails release if any embedded route, remedy, action, actor, source-currentness, or axis field drifts.

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

## Claim-provenance runtime audit

Claim runtime status: profile_index_claim_packets_emitted
Claim-bearing answer packets: 122
Claim route instances: 610
Claim packets: 2735
Required claim-type recall: 2551/2551
Claim source-edge recall: 17703/17703
Currentness claim recall: 295/295
Complete claim-packet answers: 122/122

Source IDs alone are no longer sufficient at answer time. Every selected route must now emit claim packets for route classification, policy category-error blocking, accountability assignment, remedy/default-blocked moves, and currentness claims when applicable. Each packet must name a profile field and source IDs; every primary source for the selected route must appear inside at least one claim packet.

## Profile audits

Remedy profiles: 155
Policy-action profiles: 155
Actor-accountability profiles: 155
Repository-process placeholders in remedy escalation triggers: 0
Repository-process placeholders in policy-action escalation triggers: 0

## Axis and waste audits

Declared axis values still equal live route usage plus active case-contract requirements. Rev0322 does not enlarge doctrine vocabulary; it turns existing route/profile surfaces into checked runtime output and claim provenance.

No negative bytes-saved metrics remain.

## Refactor note

`tools/answer_case.py` no longer directly joins three separate profile registries during answer emission. `tools/build_route_profile_index.py` creates the checked runtime index, `tools/audit_route_profile_index.py` blocks drift, and `tools/audit_claim_provenance.py` blocks citation theater by requiring source-backed decision claims.

## Current limitation

This is now a candidate router plus a checked profile-index-backed answer packet with claim-level provenance. It still is not a final legal or fiscal answer engine: final precedence resolution, jurisdiction-specific current-law validation, quantitative revenue/distribution/behavior/cost estimates, and human conflict resolution remain outside this runtime layer.
