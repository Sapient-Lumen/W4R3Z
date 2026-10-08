# Consolidated audit report — rev0342

Active revision: rev0342. Codename: `decision-review-bundle-handoff-promotion-refactor`. Generated: 2026-06-18T22:47:00Z.

**Interpretation rule for this report:** early execution audits retain historical labels such as “synthetic evidence satisfied” because downstream regression checks consume those exact lines. In rev0337 and later those counts mean schema/interface conformance only. Archive-generated records are never external evidence and never promotion-eligible.

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
Strict-schema test source records: 859/859
Complete reference source records: 859/859
Complete strict-schema test source records: 859/859
Implementation-grade source builder refused: yes
Strict no-source blocks: 859/859
Strict reference-fixture blocks: 859/859
Strict-schema quantitative and floor schemas satisfied: 807/807
Strict-schema no-go adapters blocked: 52/52
Strict-schema external law/jurisdiction gaps still missing: 865/865
Strict-schema local-model can-finalize answers: 0/122
Stale source-manifest blocks: 859/859
Promotion-flag tamper blocks: 859/859
Promotion-flag tamper external-attestation blocks: 859/859

Reference and strict-schema manifests are archive-generated conformance objects. The builder now raises rather than emitting `implementation_grade` source records. Quantitative and floor schemas may execute only inside the explicit strict-test context; normal execution requires externally observed, verified, promotion-eligible sources.

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
Strict-schema authority-source records: 865/865
Implementation-grade authority source builder refused: yes
Strict authority intake without source records: 0/865
Missing authority source records: 865/865
Strict-schema authority intake records: 865/865
Implementation relabel attempt intake records: 0/865
Strict authority records without intake: 0/865
Missing authority intake records: 865/865
Reference authority records: 865/865
Strict-schema authority evidence records: 865/865
Strict no-authority missing adapters: 865/865
Strict no-intake execution missing adapters: 865/865
Strict reference authority blocks: 865/865
Strict reference intake blocks: 865/865
Strict-schema authority satisfactions: 865/865
Strict-schema model/floor satisfactions preserved: 807/807
Strict-schema no-go blocks preserved: 52/52
Schema-execution can-finalize answers before promotion: 83/122
Stale authority blocks: 865/865
Promotion-flag tamper blocks: 865/865
Promotion-flag tamper external-attestation blocks: 865/865
Strict interface authority blocks: 865/865
Strict interface model blocks: 859/859

The authority source, intake, and evidence builders now distinguish reference fixtures, explicit strict-schema fixtures, and externally supplied implementation evidence. They refuse to manufacture implementation-grade authority sources. Relabeling a strict fixture as implementation grade emits no valid intake records, and ordinary strict execution requires an externally observed primary-authority source with verified attestation and a non-fixture locator.

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

`tools/answer_case.py` still delegates disposition to `tools/synthesize_disposition.py`, which delegates adapter requirements to `tools/resolve_decision_adapters.py`. Rev0339 repairs the next semantic boundary after the verifier: archive-generated fixtures may exercise execution but may not certify implementation, and future implementation evidence can no longer be replayed across adapter scopes. Evidence origin, external attestation, adapter binding, verifier status, and promotion eligibility are bound into replay records; promotion recomputes the complete ledger hash; release lineage is checked by one shared validator.

The expensive semantic audits now reuse one answer-packet cache and one strict-evidence cache, but the answer and truth-boundary groups execute each audit in an isolated process. That avoids retaining every authority, replay, promotion, and output graph inside one long-lived worker. Temporary cache and bytecode artifacts are removed before manifest generation.

## Current limitation

This is a candidate router plus checked profile-backed answer packets, claim provenance, precedence, disposition, adapter requirements, schema-conformance execution, producer work orders, replay, promotion, adapter-bound attestation verification, and held decision outputs. It is not a live-law or calibrated-model system. Real current-law retrieval, primary-authority conflict resolution, calibrated distribution/revenue/behavior/cost models, delivery validation, no-go review, a production trust-root configuration, transparency-log inclusion verification, timestamp verification, revocation monitoring, and accountable human judgment remain required before implementation.

## External-attestation verifier runtime audit

External attestation verifier runtime status: external_attestation_verifier_checked
Verifier profile: ed25519_canonical_json_v1
Valid signed evidence status: verified_external_attestation
Adapter binding replay blocked: yes
No trust store status: not_configured_fail_closed
Tampered payload status: attestation_payload_mismatch
Forged status without proof: missing_external_attestation
Expired attestation status: attestation_or_trust_entry_expired
Revoked key status: attestation_key_revoked
Transparency-required status: attestation_transparency_log_missing_or_unverified

The verifier signs and checks canonical JSON evidence-payload hashes with Ed25519. Rev0339 also requires the signed payload to bind the exact adapter scope, so evidence for one case, route, source, model, scope, or required-output set cannot be replayed into another adapter. This is not yet a production Sigstore, Rekor, RFC3161, DID, VC, or revocation implementation; it is the executable seam that prevents producer-authored status strings or cross-adapter replay from crossing into promotion without a trusted, scope-bound signature.

## Evidence replay ledger runtime audit

Evidence replay runtime status: evidence_replay_ledger_generated
Answer packets checked: 122
Adapter ledger records: 1724/1724
Strict-schema fixture records: 1724/1724
Externally observed records: 0/1724
Verified external attestation records: 0/1724
Promotion-eligible records: 0/1724
Strict model-input source proof records: 0/859
Strict authority evidence proof records: 0/865
Trusted external attestation verified records: 0/1724
Adapter binding hashes recorded: 1724/1724
External adapter binding hashes: 0/1724
Adapter binding mismatches: 0
Attestation-not-required fixture records: 1724/1724
Trusted external attestation verifier status: not_configured_fail_closed
Schema-execution finalizable cases: 83/122
Schema-execution blocked cases: 39/122
Same-bundle replay mismatches: 0
Evidence-tamper replay mismatches: 6896
Promotion-flag replay mismatches: 15464
Schema-execution status counts: executed_evidence_satisfies_adapter: 1672, executed_evidence_blocks_finalization: 52

The replay ledger now carries and hashes `adapter_binding_hash`, `evidence_adapter_binding_hash`, strict model-input and authority-evidence gate flags, strict proof hashes, `strict_schema_test_fixture`, `evidence_origin`, `external_source_attestation_status`, `external_attestation_verifier_status`, `trusted_external_attestation`, and `promotion_eligible`. The top-level ledger hash is the hash of the complete live record list. A replay-clean internal fixture remains non-promotable.

## Decision-promotion gate runtime audit

Decision promotion runtime status: decision_promotion_gate_evaluated
Answer packets checked: 122
Adapter ledger records: 1724/1724
Schema-execution finalizable cases before promotion: 83/122
Strict-schema promoted cases: 0/122
Strict-schema held cases: 122/122
Satisfied adapter records: 1672/1724
Blocked adapter records: 52/1724
Externally observed adapter records: 0/1724
Promotion-eligible adapter records: 0/1724
Cryptographically verified external attestations: 0/1724
Strict model-input source proof records: 0/859
Strict authority evidence proof records: 0/865
Adapter binding hashes recorded: 1724/1724
External adapter binding hashes: 0/1724
Adapter binding mismatches: 0
Trusted external attestation verifier status: not_configured_fail_closed
Empty-evidence promoted cases: 0/122
Interface-fixture promoted cases: 0/122
Tamper replay mismatches: 6896
Replay-tamper promoted cases: 0/122
Forged-ledger promoted cases: 0/122

Promotion now requires external observation, record eligibility, adapter-binding agreement, strict implementation-grade model-input source proof for model adapters, strict implementation-grade authority proof for current-law and jurisdiction adapters, recomputed truth-boundary hashes, a recomputed whole-ledger hash, and verification by a trusted external-attestation verifier. Rev0339 includes the adapter-bound verifier code path but does not configure production trust roots; a caller-supplied `verified_external_attestation` string without a trusted scope-bound signature is blocked before promotion, so the built-in release remains deliberately fail-closed. The structurally finalizable 83-case subset is held because its evidence is internal test data, not because its schemas failed.

## Decision-output materialization runtime audit

Decision output runtime status: decision_output_packets_materialized
Answer packets checked: 122
Adapter record hashes materialized: 1724/1724
Strict-schema finalized cases: 0/122
Strict-schema held cases: 122/122
Empty-bundle finalized cases: 0/122
Interface-fixture finalized cases: 0/122
Tamper replay mismatches: 6896
Tamper finalized cases: 0/122
Raw evidence stored: no
Decision-output status counts: held_pending_external_observed_replay_clean_evidence: 122

Decision outputs retain route, actor, remedy, hold-reason, and hash summaries without storing raw authority text or model snapshots. The built-in release audit emits only held outputs because it contains no externally observed evidence.

## Release-lineage runtime audit

Release lineage status: valid
Active revision: rev0342
Previous revision: rev0341
Canonical output zip: Moral-Taxation-rev0342-2026.06.18.22.47-decision-review-bundle-handoff-promotion-refactor.zip
Canonical archive root: moral_taxation_rev0342
Metadata timestamp agreement: yes
Context routes carry active revision only: yes
Source count agreement: 670/670

The validator derives rather than trusts the predecessor, root, and output filename. It is shared by the semantic audit, structural checker, and packager so a mutually consistent but false release history cannot pass.

## rev0339 correction note

This revision adds no routes, axes, or doctrine. It narrows the external-attestation seam by binding signed evidence to the exact adapter scope and by adding explicit trust-policy failure modes for revoked keys and transparency-required configurations. The prior verifier introduction remains in `docs/00-meta/external-attestation-verifier-refactor-rev0338.md`; the current delta is in `docs/00-meta/adapter-binding-trust-policy-promotion-refactor-rev0339.md`.

## rev0341 strict positive external evidence proof path

Positive external evidence smoke path: enabled
Smoke bundle runtime status: signed_external_evidence_smoke_bundle_generated
Smoke case: GC-001 with default route limit 5
Verified smoke adapter records: 22/22
Strict model-input source proofs: 5/5
Strict authority evidence proofs: 17/17
Replay mismatches: 0
Final promoted cases: 0
Sandbox positive-path cases: 1
Non-default route-limit production gate: blocked

Interpretation: this is an executable verifier/replay/promotion mechanics check, not a legal or model conclusion. The signed bundle is sandbox-labeled, uses the default GC-001 route set, exercises strict implementation-grade proof fields, and can never count as a final promoted case.


## Decision review bundle handoff audit

Decision review bundle runtime status: decision_review_bundle_exported
Review case: GC-001
Review adapter records: 22
Embedded attestations verified: 22/22
Strict model-input source proofs: 5/5
Strict authority evidence/source proofs: 17/17
Replay mismatches: 0
Finalized cases inside review bundle: 0
Sandbox positive-path cases inside review bundle: 1
Private key material exported: no

The decision review bundle is a hash-bound handoff artifact for re-checking signatures, adapter bindings, strict proof hashes, replay consistency, and held decision-output status. It is deliberately non-certifying: production finalization remains blocked.
