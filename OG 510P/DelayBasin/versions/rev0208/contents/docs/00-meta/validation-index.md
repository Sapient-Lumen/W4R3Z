# Validation index

This is a compact human-facing inventory for what the current checked command surface is doing.
It exists so `make lint` can stay the admission wrapper without becoming a discovery black box.

## Commands
- `python3 tools/gen_context_pack.py` — `context-pack.json`
- `python3 tools/gen_innovation_packet.py` — `innovation-packet.json`
- `python3 tools/gen_frontier_ticket.py` — `frontier-ticket.json`
- `python3 tools/gen_replay_capsule.py` — `replay-capsule.json`
- `python3 tools/gen_validation_index.py` — `VALIDATION-INDEX.json`, `docs/00-meta/validation-index.md`
- `python3 tools/gen_compact_surface_bundle.py` — `compact-surface-bundle.json`
- `python3 tools/gen_reentry_surface_conformance.py` — `REENTRY-SURFACE-CONFORMANCE.json`
- `make lint` — admission wrapper / no direct artifact
- `make package-release STAMP=... SLUG=...` — `RELEASE-MANIFEST.json`

## Coverage honesty
- This inventory names the major command surfaces and the main validation families behind `make lint`; it is not a proof graph for every single tool-level semantic distinction.
- Do not treat this surface as a workflow-state machine, lint court, or exhaustive per-check theorem map. Reopen the named governing surfaces before inheriting any stronger claim.

## Main validation families
### discovery, release identity, and package coherence
- Tool count: 6
- Coverage claim: keep named bundle lineage, release metadata, and discovery surfaces machine-checkable so the current packaged archive stays inspectable rather than recency-shaped.
- Governing surface hints: `README.md`, `docs/README.md`, `ARCHIVE_INDEX.md`, `CHANGELOG.md`, `RELEASE-MANIFEST.json`
- Representative tools: `check_discovery.py`, `check_registry_ids.py`, `check_revision_sync.py`, `check_archive_index_order.py`, `check_release_hygiene.py`, `check_frozen_head_alignment.py`

### startup and derivative packet surfaces
- Tool count: 17
- Coverage claim: keep the compact startup wrappers, current-focus packet, exact current innovation packet, bounded replay capsule, compact family card, reentry conformance, and validation inventory source-backed and derivative rather than ambient or silently stale.
- Governing surface hints: `START_HERE.md`, `AGENTS.md`, `context-pack.json`, `innovation-packet.json`, `frontier-ticket.json`, `replay-capsule.json`, `compact-surface-bundle.json`, `REENTRY-CONTRACT.json`, `REENTRY-SURFACE-CONFORMANCE.json`, `VALIDATION-INDEX.json`, `docs/00-meta/validation-index.md`
- Representative tools: `check_agents_contract.py`, `gen_context_pack.py`, `gen_innovation_packet.py`, `gen_frontier_ticket.py`, `gen_compact_surface_bundle.py`, `gen_validation_index.py`, `gen_reentry_surface_conformance.py`, `check_context_pack_budget.py`, …

### receipt, basis, scope, and status honesty
- Tool count: 13
- Coverage claim: keep revision receipts explicit about basis precision, scope, authorship, operational-vs-citation heads, status lanes, and terse-key freshness rather than letting one lively surface inherit flattering authority.
- Governing surface hints: `REVISION-RECEIPT.json`, `SURFACE-STATUS.json`, `docs/10-method/basis-witnesses-expected-head-guards-and-session-honesty-bridges.md`, `docs/10-method/status-lane-witnesses-decision-execution-splits-and-frozen-public-transitions.md`, `docs/10-method/scope-witnesses-active-request-packets-and-ambient-roster-guards.md`, `docs/10-method/authorship-witnesses-autonomy-postures-and-maker-checker-traces.md`, `docs/10-method/receipt-freshness-witnesses-bundle-stem-truth-and-carryforward-key-coherence.md`
- Representative tools: `check_basis_witness_contract.py`, `check_basis_witness_exactness.py`, `check_basis_anchor_precision_contract.py`, `check_scope_witness_contract.py`, `check_authorship_witness_contract.py`, `check_status_lane_witness_contract.py`, `check_revision_receipt_contract.py`, `check_receipt_freshness_contract.py`, …

### governed vocabularies, registries, and controlled tokens
- Tool count: 6
- Coverage claim: keep prompt pairs, moves, lexicon entries, decay watches, and witness vocabulary synchronized so later comparisons do not drift into checker-local synonyms or orphan ids.
- Governing surface hints: `WITNESS-VOCABULARY.json`, `docs/20-constitution/core-lexicon-registry.md`, `docs/20-constitution/move-registry.md`, `docs/20-constitution/prompt-pair-registry.md`, `docs/20-constitution/promotion-contract-registry.md`, `docs/20-constitution/decay-watch-registry.md`
- Representative tools: `check_prompt_pair_contract.py`, `check_core_lexicon_contract.py`, `check_move_registry_contract.py`, `check_promotion_contract.py`, `check_decay_watch_contract.py`, `check_vocabulary_witness_contract.py`

### continuity ledgers and cross-datacube transfer memory
- Tool count: 10
- Coverage claim: keep live followthrough, assumptions, obligations, imports, action lanes, gate classes, resolutions, and quarantine boundaries durable rather than scattered across revision prose.
- Governing surface hints: `FOLLOWTHROUGH-QUEUE.json`, `ASSUMPTION-LEDGER.json`, `OBLIGATION-LEDGER.json`, `FOREIGN-PRESSURE-LEDGER.json`, `DATACUBE-TRANSFER-LEDGER.json`, `RESOLUTION-LEDGER.json`, `RETROSPECTIVE-QUEUE.json`, `FIREBREAK-LEDGER.json`
- Representative tools: `check_followthrough_witness_contract.py`, `check_assumption_witness_contract.py`, `check_obligation_witness_contract.py`, `check_foreign_pressure_witness_contract.py`, `check_transfer_ledger_contract.py`, `check_import_hygiene_contract.py`, `check_action_lane_contract.py`, `check_gate_class_contract.py`, …

### GPUstorming handle-family controls
- Tool count: 3
- Coverage claim: keep the accumulated exact-handle anti-overclaim and anti-derivative-laundering ratchets synchronized across method, promptcraft, trajectory, and registry surfaces.
- Governing surface hints: `docs/10-method/gpustorming-control-family-crosswalk-and-sync-guards.md`, `docs/50-promptcraft/prompt-pairs.md`, `docs/20-constitution/claim-registry.md`, `docs/20-constitution/open-question-registry.md`
- Representative tools: `check_gpustorming_scopenarrow_contract.py`, `check_gpustorming_claimceiling_contract.py`, `check_sink_namespace_contract.py`

### broader method witness families
- Tool count: 115
- Coverage claim: keep the large witness and packet families in docs/10-method tied to their registries, prompts, and receipts so make lint does not collapse into one opaque green light.
- Governing surface hints: `docs/10-method/`, `docs/20-constitution/claim-registry.md`, `docs/20-constitution/invariant-registry.md`, `docs/20-constitution/open-question-registry.md`, `docs/50-promptcraft/prompt-pairs.md`
- Representative tools: `check_bibliography_contract.py`, `gen_replay_capsule.py`, `check_replay_capsule_contract.py`, `check_recovery_kernel_contract.py`, `check_counterfactual_shadow_contract.py`, `check_regime_probe_contract.py`, `check_public_hidden_state_contract.py`, `check_belief_state_contract.py`, …
