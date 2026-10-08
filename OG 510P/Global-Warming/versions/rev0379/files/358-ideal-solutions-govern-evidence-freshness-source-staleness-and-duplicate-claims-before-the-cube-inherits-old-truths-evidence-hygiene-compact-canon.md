---
id: '358'
revision_added: rev0276
status: canon
object_type: ledger
domain_tags:
- evidence_hygiene
- source_register
- freshness
- staleness
- duplicate_sources
- citation_policy
- audit
service_floor:
- source_freshness_review
- duplicate_source_collapse
- stale_claim_demote
- citation_to_ledger
hazard_tags:
- all_hazards
- trend_change
- policy_change
- technology_change
- market_change
clock_tags:
- learning_clock
- finance_clock
- stock_turnover_clock
actor_tags:
- maintainer
- source_steward
- domain_reviewer
- auditor
- reader
instrument_tags:
- review
- deduplicate
- supersede
- quarantine
- refresh
- annotate
- demote
routes_to:
- '301'
- '302'
- '322'
- '356'
source_ids:
- S654
- S663
- S667
upstream_dependencies:
- source_register
- used_by_index
- domain_reviewer
- web_refresh
- claim_to_source_mapping
downstream_consequences:
- stale_recommendations
- false_confidence
- duplicated_evidence
- policy_misapplication
- untraceable_claims
equity_lenses:
- jurisdictions_with_fast_policy_change
- low_data_contexts
- non_english_sources
- indigenous_and_local_knowledge
- grey_literature_dependence
degraded_modes:
- mark_claim_stale_not_wrong
- route_to_refresh_queue
- cap_readiness_score
- quarantine_uncited_source
- cite_stable_boundary_condition
evidence_grade: design_judgment
speculation_level: medium
bottlenecks:
- new_upload_of_old_source
- recent_modified_date_misread_as_current
- duplicate_register_entry
- source_cited_for_more_than_it_supports
- stale_policy_rule
- dead_link
failure_modes:
- old_fact_becomes_current_rule
- duplicate_sources_inflate_evidence_weight
- citation_footer_hides_late_addendum
- source_register_grows_without_used_by
- claim_outlives_original_context
proof_ledgers:
- source_freshness_dashboard
- duplicate_source_map
- superseded_by_field
- used_by_index
- claim_review_log
- dead_link_check
restoration_conflicts:
- stable_science_vs_fast_policy
- source_authority_vs_recency
- primary_source_vs_synthesis
- copyright_limits_vs_traceability
assurance_tests:
- random_citation_pull
- latest_source_check
- duplicate_cluster_review
- source_claim_alignment_test
- dead_link_scan
evidence_freshness: claims_get_review_cadence_and_stale_sources_cap_readiness_scores
---

# 358 — Ideal Solutions: Govern evidence freshness, source staleness, and duplicate claims before the cube inherits old truths

## Claim

A datacube can make old information more dangerous by making it easier to reuse. Once a claim becomes a field, route, score, or checklist item, readers may treat it as live even after policy, markets, technology, hazard data, or institutional capacity change.

The archive already distinguishes constraint, trend, and support citations. Rev0276 turns that habit into an evidence hygiene rule: **every claim type needs a freshness clock, and stale evidence should cap readiness scores.**

## Fast rule

Use four freshness classes:

- **F0 — structural constraint:** slow-moving science or physics; review on major assessment cycles.
- **F1 — stable doctrine:** governance or design principle; review when contradicted by events.
- **F2 — active policy / market:** law, finance, insurance, programme, or technology; review at least annually.
- **F3 — live operations:** prices, eligibility rules, hazard alerts, schedules, contacts, inventories, and owners; review before use.

A file can cite stable science and still contain stale implementation claims.

## The compact canon

### 1. Source age is not the same as claim age

A 2023 synthesis may remain the right climate constraint. A 2025 programme page may already be wrong if eligibility changed. A recently modified file may preserve a decade-old claim. The cube should attach freshness to the claim, not simply to the source metadata.

### 2. Duplicates should not become weight

Repeated entries for the same IEA, UNEP, World Bank, FEMA, or UN document should collapse into one canonical source ID with aliases. Duplicate citation should not imply independent confirmation.

### 3. Evidence grades should limit score grades

A service floor supported only by design judgment may still be worth piloting, but it should not receive R4 maturity without local test evidence. A stale market source should cap insurance, finance, and supply-chain readiness until refreshed.

### 4. "Used by" is a maintenance tool

Each source should know where it is used. When a source is superseded or found unreliable, the maintainer should be able to find all dependent files, fields, and scores.

### 5. Quarantine is better than silent deletion

Bad, stale, overclaimed, or speculative sources should be marked, explained, and routed away from operational decisions. Deleting them can hide why a claim changed.

## Minimum packet

An evidence-hygiene packet includes: source ID; canonical source; aliases; publication date; accessed date; source type; evidence role; freshness class; next review date; used-by files; supersedes / superseded-by; link status; and claim-specific notes where the source is being stretched.

## Bottom line

A cube is only as current as its weakest reused claim. The archive should demote stale evidence, collapse duplicates, and make source maintenance visible enough to govern.

## Rev0277 evidence extension: live data products decay too

Evidence freshness now applies to dashboards, telemetry, remote-sensing products, rumor pages, OT inventories, toxic-site overlays, and disease-surveillance feeds. A live dashboard can become stale faster than a synthesis report. A sensor map can become misleading when calibration, power, or connectivity fails.

Add a data-product freshness class: `D0_missing`, `D1_snapshot`, `D2_maintained`, `D3_live_with_gap_flags`, and `D4_live_contestable`. Route to `365`, `366`, and `371` [S654][S663][S667].

---
Citations point to `sources/register.md`.
