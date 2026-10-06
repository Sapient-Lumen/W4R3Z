# Validation index

This is a compact human-facing inventory for what the current checked command surface is doing.
It exists so `make lint` can stay the admission wrapper without becoming a discovery black box.

## Commands
- `python3 tools/gen_all_generated_surfaces.py` — `LICENSE`, `CITATION.cff`, `codemeta.json`, `ro-crate-metadata.json`, `SBOM.spdx.json`, `context-pack.json`, `innovation-packet.json`, `frontier-ticket.json`, `replay-capsule.json`, `compact-surface-bundle.json`, `CANARY-RUNS.json`, `VALIDATION-INDEX.json`, `VALIDATION-TOOLCHAIN-MANIFEST.json`, `LINT-IDEMPOTENCE-AUDIT.json`, `CURRENTNESS-CUE-AUDIT.json`, `PACKAGE-IDENTITY-AUDIT.json`, `BASIS-PROVENANCE-AUDIT.json`, `SCHEMA-COVERAGE-AUDIT.json`, `SCHEMA-CONFORMANCE-AUDIT.json`, `REENTRY-SURFACE-CONFORMANCE.json`, `LEDGER-AUDIT.json`, `ARCHIVE-ECONOMY-AUDIT.json`, `FILE-MANIFEST.json`, `CHECKSUMS.sha256`, `RELEASE-PROVENANCE.json`
- `python3 tools/gen_external_metadata.py` — `LICENSE`, `CITATION.cff`, `codemeta.json`, `ro-crate-metadata.json`, `SBOM.spdx.json`
- `python3 tools/gen_context_pack.py` — `context-pack.json`
- `python3 tools/gen_innovation_packet.py` — `innovation-packet.json`
- `python3 tools/gen_frontier_ticket.py` — `frontier-ticket.json`
- `python3 tools/gen_replay_capsule.py` — `replay-capsule.json`
- `python3 tools/gen_validation_index.py` — `VALIDATION-INDEX.json`, `docs/00-meta/validation-index.md`
- `python3 tools/gen_validation_toolchain_manifest.py` — `VALIDATION-TOOLCHAIN-MANIFEST.json`, `docs/00-meta/validation-toolchain.md`
- `python3 tools/gen_currentness_cue_audit.py` — `CURRENTNESS-CUE-AUDIT.json`, `docs/00-meta/currentness-cue-audit.md`
- `python3 tools/gen_package_identity_audit.py` — `PACKAGE-IDENTITY-AUDIT.json`, `docs/00-meta/package-identity-audit.md`
- `python3 tools/gen_basis_provenance_audit.py` — `BASIS-PROVENANCE-AUDIT.json`, `docs/00-meta/basis-provenance-audit.md`
- `python3 tools/gen_schema_coverage_audit.py` — `SCHEMA-COVERAGE-AUDIT.json`, `docs/00-meta/schema-coverage-audit.md`
- `python3 tools/gen_schema_conformance_audit.py` — `SCHEMA-CONFORMANCE-AUDIT.json`, `docs/00-meta/schema-conformance-audit.md`
- `python3 tools/gen_lint_idempotence_audit.py` — `LINT-IDEMPOTENCE-AUDIT.json`, `docs/00-meta/lint-idempotence-audit.md`
- `python3 tools/gen_compact_surface_bundle.py` — `compact-surface-bundle.json`
- `python3 tools/gen_canary_runs.py` — `CANARY-RUNS.json`
- `python3 tools/gen_reentry_surface_conformance.py` — `REENTRY-SURFACE-CONFORMANCE.json`
- `python3 tools/gen_release_integrity.py` — `FILE-MANIFEST.json`, `CHECKSUMS.sha256`, `RELEASE-PROVENANCE.json`
- `python3 tools/gen_ledger_audit.py` — `LEDGER-AUDIT.json`, `docs/00-meta/ledger-audit.md`
- `python3 tools/gen_archive_economy_audit.py` — `ARCHIVE-ECONOMY-AUDIT.json`, `docs/00-meta/archive-economy-audit.md`
- `make lint` — admission wrapper / no direct artifact
- `make package-release STAMP=... SLUG=...` — `RELEASE-MANIFEST.json`

## Coverage honesty
- This inventory names the major command surfaces and the main validation families behind `make lint`; it is not a proof graph for every single tool-level semantic distinction.
- Do not treat this surface as a workflow-state machine, lint court, or exhaustive per-check theorem map. Reopen the named governing surfaces before inheriting any stronger claim.

## Main validation families
### discovery, release identity, and package coherence
- Tool count: 28
- Coverage claim: keep named bundle lineage, release metadata, and discovery surfaces machine-checkable so the current packaged archive stays inspectable rather than recency-shaped.
- Governing surface hints: `README.md`, `docs/README.md`, `ARCHIVE_INDEX.md`, `CHANGELOG.md`, `RELEASE-MANIFEST.json`, `FILE-MANIFEST.json`, `CHECKSUMS.sha256`, `RELEASE-PROVENANCE.json`, `CANARY-PROTOCOL.json`, `CANARY-RUNS.json`, `LEDGER-AUDIT.json`, `docs/00-meta/ledger-audit.md`, `VALIDATION-TOOLCHAIN-MANIFEST.json`, `docs/00-meta/validation-toolchain.md`, `CURRENTNESS-CUE-AUDIT.json`, `docs/00-meta/currentness-cue-audit.md`, `PACKAGE-IDENTITY-AUDIT.json`, `docs/00-meta/package-identity-audit.md`, `SCHEMA-CONFORMANCE-AUDIT.json`, `docs/00-meta/schema-conformance-audit.md`, `SCHEMA-COVERAGE-AUDIT.json`, `docs/00-meta/schema-coverage-audit.md`, `ALIAS-RETENTION-POLICY.json`, `CANARY-RUNS.json`
- Representative tools: `check_discovery.py`, `check_registry_ids.py`, `check_revision_sync.py`, `check_archive_index_order.py`, `check_archive_index_table_shape.py`, `check_release_hygiene.py`, `check_internal_surface_references.py`, `check_path_portability_contract.py`, …

### startup and derivative packet surfaces
- Tool count: 14
- Coverage claim: keep the compact startup wrappers, current-focus packet, exact current innovation packet, bounded replay capsule, compact family card, reentry conformance, and validation inventory source-backed and derivative rather than ambient or silently stale.
- Governing surface hints: `START_HERE.md`, `AGENTS.md`, `context-pack.json`, `innovation-packet.json`, `frontier-ticket.json`, `replay-capsule.json`, `compact-surface-bundle.json`, `REENTRY-CONTRACT.json`, `REENTRY-SURFACE-CONFORMANCE.json`, `VALIDATION-INDEX.json`, `docs/00-meta/validation-index.md`, `VALIDATION-TOOLCHAIN-MANIFEST.json`, `docs/00-meta/validation-toolchain.md`, `CURRENTNESS-CUE-AUDIT.json`, `docs/00-meta/currentness-cue-audit.md`, `SCHEMA-CONFORMANCE-AUDIT.json`, `docs/00-meta/schema-conformance-audit.md`, `SCHEMA-COVERAGE-AUDIT.json`, `docs/00-meta/schema-coverage-audit.md`
- Representative tools: `check_agents_contract.py`, `check_context_pack_budget.py`, `check_release_integrity_contract.py`, `check_context_pack_fidelity.py`, `check_context_pack_contract.py`, `check_current_innovation_packet_contract.py`, `check_frontier_ticket_contract.py`, `check_compact_surface_bundle_contract.py`, …

### receipt, basis, scope, and status honesty
- Tool count: 17
- Coverage claim: keep revision receipts explicit about basis precision, scope, authorship, operational-vs-citation heads, status lanes, and terse-key freshness rather than letting one lively surface inherit flattering authority.
- Governing surface hints: `REVISION-RECEIPT.json`, `SURFACE-STATUS.json`, `docs/10-method/basis-witnesses-expected-head-guards-and-session-honesty-bridges.md`, `docs/10-method/status-lane-witnesses-decision-execution-splits-and-frozen-public-transitions.md`, `docs/10-method/scope-witnesses-active-request-packets-and-ambient-roster-guards.md`, `docs/10-method/authorship-witnesses-autonomy-postures-and-maker-checker-traces.md`, `docs/10-method/receipt-freshness-witnesses-bundle-stem-truth-and-carryforward-key-coherence.md`
- Representative tools: `check_basis_provenance_witness_contract.py`, `check_basis_provenance_currentness_contract.py`, `check_basis_provenance_audit_contract.py`, `check_basis_witness_contract.py`, `check_basis_witness_exactness.py`, `check_basis_anchor_precision_contract.py`, `check_scope_witness_contract.py`, `check_authorship_witness_contract.py`, …

### governed vocabularies, registries, and controlled tokens
- Tool count: 6
- Coverage claim: keep prompt pairs, moves, lexicon entries, decay watches, and witness vocabulary synchronized so later comparisons do not drift into checker-local synonyms or orphan ids.
- Governing surface hints: `WITNESS-VOCABULARY.json`, `docs/20-constitution/core-lexicon-registry.md`, `docs/20-constitution/move-registry.md`, `docs/20-constitution/prompt-pair-registry.md`, `docs/20-constitution/promotion-contract-registry.md`, `docs/20-constitution/decay-watch-registry.md`
- Representative tools: `check_prompt_pair_contract.py`, `check_core_lexicon_contract.py`, `check_move_registry_contract.py`, `check_promotion_contract.py`, `check_decay_watch_contract.py`, `check_vocabulary_witness_contract.py`

### continuity ledgers and cross-datacube transfer memory
- Tool count: 11
- Coverage claim: keep live followthrough, assumptions, obligations, imports, action lanes, gate classes, resolutions, and quarantine boundaries durable rather than scattered across revision prose.
- Governing surface hints: `FOLLOWTHROUGH-QUEUE.json`, `ASSUMPTION-LEDGER.json`, `OBLIGATION-LEDGER.json`, `FOREIGN-PRESSURE-LEDGER.json`, `DATACUBE-TRANSFER-LEDGER.json`, `RESOLUTION-LEDGER.json`, `RETROSPECTIVE-QUEUE.json`, `FIREBREAK-LEDGER.json`
- Representative tools: `check_self_sufficiency_assay_contract.py`, `check_followthrough_witness_contract.py`, `check_assumption_witness_contract.py`, `check_obligation_witness_contract.py`, `check_foreign_pressure_witness_contract.py`, `check_transfer_ledger_contract.py`, `check_import_hygiene_contract.py`, `check_action_lane_contract.py`, …

### GPUstorming handle-family controls
- Tool count: 9
- Coverage claim: keep the accumulated exact-handle anti-overclaim and anti-derivative-laundering ratchets synchronized across method, promptcraft, trajectory, and registry surfaces.
- Governing surface hints: `docs/10-method/gpustorming-control-family-crosswalk-and-sync-guards.md`, `docs/50-promptcraft/prompt-pairs.md`, `docs/20-constitution/claim-registry.md`, `docs/20-constitution/open-question-registry.md`
- Representative tools: `check_gpustorming_contract.py`, `check_gpustorming_registry_contract.py`, `check_gpustorming_standard_family_batch_contract.py`, `check_gpustorming_late_search_family_batch_contract.py`, `check_gpustorming_crosswalk_contract.py`, `check_gpustorming_late_search_sync.py`, `check_gpustorming_path_sync.py`, `check_gpustorming_problem_chain_sync.py`, …

### broader method witness families
- Tool count: 132
- Coverage claim: keep the large witness and packet families in docs/10-method tied to their registries, prompts, and receipts so make lint does not collapse into one opaque green light.
- Governing surface hints: `docs/10-method/`, `docs/20-constitution/claim-registry.md`, `docs/20-constitution/invariant-registry.md`, `docs/20-constitution/open-question-registry.md`, `docs/50-promptcraft/prompt-pairs.md`
- Representative tools: `check_release_hygiene_relative_root.py`, `check_release_identity_canaries.py`, `check_path_alias_ledger_contract.py`, `check_path_alias_witness_contract.py`, `check_alias_retention_policy_contract.py`, `check_alias_retention_witness_contract.py`, `check_generated_surface_nonmutation_canary.py`, `check_package_release_preflight_contract.py`, …
