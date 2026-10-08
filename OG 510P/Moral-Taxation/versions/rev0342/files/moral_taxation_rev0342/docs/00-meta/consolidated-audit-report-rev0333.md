> **Superseded evidence-status notice (rev0337):** This historical report treated archive-generated deterministic fixtures as implementation-grade evidence. Its implementation, promotion, or finalization counts demonstrate schema conformance only, not externally observed facts or authority. Use [the rev0337 truth-boundary report](evidence-truth-boundary-release-lineage-refactor-rev0337.md) for current status.

# Consolidated audit report — rev0333

Active revision: rev0333. Codename: `authority-source-manifest-strict-intake-refactor`. Generated: 2026-06-18T19:29:00Z.

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
Synthetic-evidence registered producer results: 1724/1724
Adapter-execution type counts: current_law_refresh_adapter: 295, floor_delivery_adapter: 388, jurisdiction_scope_adapter: 570, no_go_threshold_adapter: 52, quantitative_model_adapter: 419
Empty-evidence status counts: blocked_missing_external_evidence: 1724
Synthetic-evidence status counts: executed_evidence_satisfies_adapter: 1724

Adapter execution remains separate from adapter requirement generation. Empty external evidence blocks finalization for every current-law, jurisdiction-scope, quantitative-model, floor-delivery, and no-go adapter. Complete evidence-shaped bundles now satisfy the interface only when they identify a registered producer contract; the archive still does not fetch live law, run fiscal models, or treat old source citations as current legal advice.

## Evidence-producer contract and request audit

Evidence-producer runtime status: evidence_producer_contracts_checked
Evidence-producer contracts: 5
Adapter types covered: 5/5
Evidence requests planned: 1724/1724
Evidence requests with producer coverage: 1724/1724
Evidence requests with lookup keys: 1724/1724
Evidence requests external-only: 1724/1724
Evidence requests requiring explicit model inputs: 859/859
Evidence requests requiring implementation-grade authority evidence: 865/865
Evidence requests requiring raw authority intake: 865/865
Evidence requests requiring authority-source manifests: 865/865
Registered-producer synthetic evidence satisfied adapters: 1724/1724
Registered-producer synthetic evidence can-finalize answers: 122/122
Invalid-producer evidence blocked adapters: 1724/1724
Invalid-producer can-finalize answers: 0/122
Evidence request type counts: current_law_refresh_adapter: 295, floor_delivery_adapter: 388, jurisdiction_scope_adapter: 570, no_go_threshold_adapter: 52, quantitative_model_adapter: 419
Evidence request producer counts: current_law_authority_retriever: 295, fiscal_incidence_model_runner: 419, jurisdiction_scope_resolver: 570, no_go_threshold_reviewer: 52, protected_floor_delivery_model_runner: 388
Registered evidence producer counts: current_law_authority_retriever: 295, fiscal_incidence_model_runner: 419, jurisdiction_scope_resolver: 570, no_go_threshold_reviewer: 52, protected_floor_delivery_model_runner: 388

The producer layer is a narrow waist, not a new doctrine registry. `docs/00-meta/evidence-producer-contracts.json` identifies which outside producer may satisfy each adapter type; `tools/plan_adapter_evidence_requests.py` turns adapter checks into external work orders; `tools/execute_decision_adapters.py` blocks bundles from unregistered producers.

## Model-input bundle audit

Model-input runtime status: explicit_model_input_bundle_generated
Answer packets checked: 122
Model adapter checks: 859
Model input records: 859/859
Complete model input records: 859/859
No-input local-model evidence produced: 0/0
Explicit-input local-model evidence produced: 859/859
Explicit-input model adapters satisfied: 807/807
Explicit-input no-go adapters blocked: 52/52
Legacy shape-only model evidence blocked: 859/859
Model input adapter type counts: floor_delivery_adapter: 388, no_go_threshold_adapter: 52, quantitative_model_adapter: 419

The model-input bundle is the new anti-fixture boundary. Local model evidence must be based on explicit input records with values, units, assumptions, uncertainty parameters, locators, and stable hashes. A runner with no model-input bundle now produces zero model evidence, and legacy shape-only evidence is blocked for every quantitative, floor-delivery, and no-go adapter.

## Model-input source certification audit

Model-input source runtime status: model_input_source_manifest_generated
Answer packets checked: 122
Model adapter checks: 859
Reference source records: 859/859
Implementation-grade source records: 859/859
Complete reference source records: 859/859
Complete implementation source records: 859/859
Strict no-source blocks: 859/859
Strict reference-fixture blocks: 859/859
Implementation-grade model adapters satisfied: 807/807
Implementation-grade no-go adapters blocked: 52/52
Implementation-grade external law/jurisdiction gaps still missing: 865/865
Implementation-grade local-model can-finalize answers: 0/122
Stale source-manifest blocks: 859/859

Rev0330 adds a source/provenance manifest boundary after explicit model-input bundles. Reference fixtures remain useful for interface tests, but strict execution blocks them as `blocked_model_input_source_not_certified`; only implementation-grade input-source manifests can satisfy quantitative and floor-delivery model adapters, and no-go/local-law/jurisdiction gaps continue to block finalization.

## Evidence-producer execution audit

Evidence-producer runner runtime status: evidence_producer_runner_invoked
Answer packets checked: 122
Adapter checks: 1724
Explicit model input records: 859/859
Interface-fixture evidence produced: 1724/1724
Interface-fixture satisfied adapters: 1724/1724
No-input local-model evidence produced: 0/0
No-input local-model skipped adapters: 1724/1724
Local-model evidence produced: 859/859
Local-model external adapters skipped: 865/865
Local-model satisfied adapters: 807/807
Local-model missing external adapters: 865/865
Local-model no-go blocks: 52/52
Legacy shape-only model evidence blocked: 859/859
Local-model can-finalize answers: 0/122
Stale-evidence blocked adapters: 1724/1724
Jurisdiction uncertain-scope block count: 1

The producer runner is reusable runtime code, not an audit-only helper. Its local model mode can no longer fabricate outputs from adapter ids or route shape alone: it requires an explicit model-input bundle. With those inputs it can satisfy quantitative and floor-delivery adapter fields, but it still leaves current-law and jurisdiction adapters missing and returns uncertain no-go screens that block finalization. The executor also blocks stale evidence, unresolved jurisdiction conflicts, and legacy model evidence without input-hash proof.

## Authority-evidence strict execution audit

Authority evidence runtime status: authority_evidence_bundle_generated
Authority intake runtime status: authority_intake_bundle_generated
Authority source runtime status: authority_intake_source_manifest_generated
Answer packets checked: 122
Authority adapter checks: 865
Current-law authority checks: 295
Jurisdiction-scope authority checks: 570
Implementation authority-source records: 865/865
Reference authority-source records: 865/865
Implementation authority intake without source records: 0/865
Missing authority source records: 865/865
Implementation authority intake records: 865/865
Reference authority intake records: 865/865
Implementation authority records without intake: 0/865
Missing authority intake records: 865/865
Reference authority records: 865/865
Implementation authority records with intake: 865/865
Strict no-authority missing adapters: 865/865
Strict no-intake implementation missing adapters: 865/865
Strict reference authority blocks: 865/865
Strict reference intake blocks: 865/865
Strict corrupt intake blocks: 865/865
Implementation authority satisfactions: 865/865
Implementation-grade model/floor satisfactions preserved: 807/807
Implementation no-go blocks preserved: 52/52
Implementation authority + model can-finalize answers: 83/122
Stale authority blocks: 865/865
Strict interface authority blocks: 865/865
Strict interface model blocks: 859/859
Strict interface can-finalize answers: 0/122

## What changed

Rev0332 required raw authority-intake records before strict current-law or jurisdiction evidence could clear. Rev0333 moves one boundary earlier: implementation-grade raw intake now requires an authority-source manifest. The source manifest records the retrieval source locator, source-record hash, retrieval claim locator, source certification level, primary-authority status, freshness, conflict-review hash, provenance hash, and non-doctrine warning.

`tools/build_authority_intake_source_manifest.py` defines that source/provenance interface. `tools/build_authority_intake_bundle.py` now emits zero implementation-grade intake records without it. `tools/build_authority_evidence_bundle.py` carries the source-manifest proof into the authority evidence bundle, and `tools/execute_decision_adapters.py` blocks strict execution when the source proof is missing, stale, reference-like, or not primary-authority certified.

Authority evidence now has a three-step implementation boundary. `tools/build_authority_intake_source_manifest.py` supplies source/provenance proof; `tools/build_authority_intake_bundle.py` supplies raw authority-intake records; `tools/build_authority_evidence_bundle.py` emits implementation-grade current-law and jurisdiction evidence only when both source and intake records are present. Shape-derived implementation intake now emits zero raw records and strict execution leaves every authority adapter missing until source-backed intake exists.

## Profile audits

Remedy profiles: 155
Policy-action profiles: 155
Actor-accountability profiles: 155
Repository-process placeholders in remedy escalation triggers: 0
Repository-process placeholders in policy-action escalation triggers: 0

## Axis and waste audits

Declared axis values still equal live route usage plus active case-contract requirements. Rev0333 does not add route, source, or axis vocabulary; it tightens the authority execution boundary by blocking interface, reference, stale, missing-source, missing-intake, and non-primary current-law or jurisdiction evidence under strict execution.

No negative bytes-saved metrics remain.

## Refactor note

`tools/answer_case.py` delegates final disposition to `tools/synthesize_disposition.py`, which delegates adapter requirements to `tools/resolve_decision_adapters.py`; adapter execution remains a separate evidence-validation boundary in `tools/execute_decision_adapters.py`. Rev0329 adds `tools/build_model_input_bundle.py`; Rev0330 adds `tools/build_model_input_source_manifest.py` and `tools/audit_model_input_source_manifests.py`; Rev0333 adds `tools/build_authority_intake_source_manifest.py`, refactors `tools/build_authority_intake_bundle.py`, and tightens execution so implementation-grade authority intake is source-manifest-bound rather than adapter-shape-bound. Finalization now also blocks stale evidence, unresolved jurisdiction scope, and model outputs without explicit input-hash proof.

The audit target removes Python bytecode/cache artifacts before manifest generation, preserving the release rule that runtime imports must not contaminate the package.

Answer-dependent semantic audits share a single cached answer-packet payload during `tools/run_semantic_audits.py`, so the output checks do not multiply expensive answer generation across the release suite.

## Current limitation

This is now a candidate router plus checked profile-index-backed answer packets with claim-level provenance, precedence resolution, final disposition synthesis, decision-adapter requirements, adapter-execution evidence validation, registered evidence-producer request gates, a reusable producer runner, explicit model-input source certification, and strict authority evidence gating, and authority-source manifest gating plus raw authority-intake provenance gating. It still is not jurisdiction-specific legal advice: external live-law retrieval, real jurisdiction conflict resolution, live authority retrieval, calibrated revenue/distribution/behavior/cost model inputs and outputs, no-go review, and human conflict judgment remain required before implementation.
