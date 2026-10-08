# Consolidated audit report — rev0326

Active revision: rev0326. Codename: `adapter-execution-evidence-boundary-refactor`. Generated: 2026-06-18T14:14:00Z.

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

The answer emitter consumes a generated runtime index that joins route, remedy, policy-action, and actor-accountability profiles once at build time. The source surfaces remain authoritative: the index stores input hashes, mirrors every live route, and fails release if any embedded route, remedy, action, actor, source-currentness, path, or axis field drifts.

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

Every selected route must emit claim packets for route classification, policy category-error blocking, accountability assignment, remedy/default-blocked moves, and currentness claims when applicable. Each packet must name a profile field and source IDs; every primary source for the selected route must appear inside at least one claim packet.

## Precedence-resolution runtime audit

Precedence runtime status: precedence_resolver_invoked
Precedence answer packets: 122
Precedence route instances: 610
Precedence ordered cases: 122/122
Precedence sorted cases: 122/122
Precedence changed candidate order: 44
Precedence triggered-rule cases: 97
Precedence triggered rules: 279
Currentness gate cases: 68
No-go gate cases: 39
Precedence band counts: 10: 52, 15: 25, 20: 451, 30: 71, 40: 11

Triggered precedence rules:
- `actor_assignment_before_liability_collection_or_compensation`: 76
- `contest_record_and_measurement_before_finality_or_penalty`: 58
- `currentness_and_release_integrity_before_final_answer`: 7
- `floor_before_collection_fee_penalty_or_forfeiture`: 56
- `no_go_before_pricing_or_compensation`: 29
- `ordinary_revenue_classification_after_no_go_floor_and_actor_checks`: 53

Candidate score selects relevance; precedence bands select decision order.

## Disposition-synthesis runtime audit

Disposition runtime status: final_disposition_synthesizer_invoked
Disposition answer packets: 122
Disposition packets: 122/122
Disposition ordered packets: 122/122
Disposition sequence-complete packets: 122/122
Hard-block recall: 897/897
Default-move route recall: 610/610
Actor-assignment route recall: 610/610
Source recall: 3311/3311
Currentness-check recall: 281/281
Quantitative-check recall: 401/401
No-go gate recall: 39/39
Cannot-finalize recall: 606/606
Dominant disposition counts: assign_real_actor_controller_or_beneficiary_before_liability: 9, block_pricing_or_offset_until_no_go_harm_is_resolved: 39, calibrate_revenue_or_compensation_after_gates: 1, check_current_sources_before_final_answer: 46, classify_and_apply_profile_default_moves_with_guardrails: 1, protect_floor_access_or_due_process_before_collection: 26

The final synthesizer converts ordered answer packets into a deterministic disposition: hard blocks, default moves, actor assignments, currentness checks, quantitative/model checks, source coverage, and cannot-finalize conditions. It is checked independently of case contracts and fails release if final output loses the obligations carried by routing, profiles, provenance, or precedence.

## Decision-adapter runtime audit

Decision-adapter runtime status: decision_adapter_requirements_resolved
Decision-adapter answer packets: 122
Adapter packets: 122/122
Complete adapter answers: 122/122
Adapter route instances: 610
Adapter check recall: 1724/1724
Current-law adapter recall: 295/295
Due-soon current-law adapter recall: 15/15
Jurisdiction adapter recall: 570/570
Quantitative adapter recall: 419/419
Floor-delivery adapter recall: 388/388
No-go-threshold adapter recall: 52/52
Adapter cannot-finalize recall: 445/445
Adapter type counts: current_law_refresh_adapter: 295, floor_delivery_adapter: 388, jurisdiction_scope_adapter: 570, no_go_threshold_adapter: 52, quantitative_model_adapter: 419
Current-law review-due states: due_soon: 15, not_due_yet: 280

Decision adapters are now part of final output. They identify the live-law refreshes, jurisdiction/effective-date checks, protected-floor delivery validations, no-go threshold reviews, and quantitative models required before implementation. The audit recomputes the adapter set from selected route packets and the source-currentness registry without reading case contracts.

## Adapter-execution runtime audit

Adapter-execution runtime status: decision_adapter_execution_evidence_checked
Adapter-execution answer packets: 122
Adapter-execution adapter checks: 1724
Empty-evidence missing adapters: 1724/1724
Empty-evidence blocked adapters: 1724/1724
Empty-evidence can-finalize answers: 0/122
Empty-evidence cannot-finalize markers: 1724/1724
Synthetic-evidence satisfied adapters: 1724/1724
Synthetic-evidence can-finalize answers: 122/122
Adapter-execution type counts: current_law_refresh_adapter: 295, floor_delivery_adapter: 388, jurisdiction_scope_adapter: 570, no_go_threshold_adapter: 52, quantitative_model_adapter: 419
Empty-evidence status counts: blocked_missing_external_evidence: 1724
Synthetic-evidence status counts: executed_evidence_satisfies_adapter: 1724

Adapter execution is now separate from adapter requirement generation. Empty external evidence blocks finalization for every current-law, jurisdiction-scope, quantitative-model, floor-delivery, and no-go adapter. Complete evidence-shaped bundles can satisfy the interface, but the archive still does not fetch live law, run fiscal models, or treat old source citations as current legal advice.

## Profile audits

Remedy profiles: 155
Policy-action profiles: 155
Actor-accountability profiles: 155
Repository-process placeholders in remedy escalation triggers: 0
Repository-process placeholders in policy-action escalation triggers: 0

## Axis and waste audits

Declared axis values still equal live route usage plus active case-contract requirements. Rev0326 does not add route, source, or axis vocabulary; it extracts and audits the adapter-execution evidence boundary after adapter requirement resolution.

No negative bytes-saved metrics remain.

## Refactor note

`tools/answer_case.py` now delegates final disposition to `tools/synthesize_disposition.py`, which delegates adapter requirements to `tools/resolve_decision_adapters.py`; adapter execution is a separate evidence-validation boundary in `tools/execute_decision_adapters.py`. The answer layer no longer leaves current law and modeling as generic unknowns; it emits auditable adapter obligations and cannot-finalize markers.


The audit target now removes Python bytecode/cache artifacts before manifest generation, preserving the release rule that runtime imports must not contaminate the package.

Answer-dependent semantic audits now share a single cached answer-packet payload during `tools/run_semantic_audits.py`, so the new final-output check does not multiply expensive answer generation across the release suite.

## Current limitation

This is now a candidate router plus checked profile-index-backed answer packets with claim-level provenance, precedence resolution, final disposition synthesis, decision-adapter requirements, and adapter-execution evidence validation. It still is not jurisdiction-specific legal advice or a fiscal model: external live-law evidence, real revenue/distribution/behavior/cost model outputs, and human conflict judgment remain required before implementation.
