# Rematch-world benchmark claim frontier

Focus: classify each first-publication rematch-world claim family as already safe now, unlocked by a concrete cumulative native-fill frontier, or still blocked by the cross-section engine gap

Generated readiness frontier for the first endogenous rematch-world benchmark. Use it to answer, in one small receipt, which claim families are already safe to cite now, which ones unlock after concrete native-fill stages, and which ones stay blocked by the cross-section engine gap.

## Main findings

- 2 claim families are already safe to cite now, 3 unlock at concrete native frontiers, and 3 remain blocked by `SG-003`.
- The actionable cumulative native claim frontiers are 8, 18, 29 edits — not 7/17/28 — because the benchmark-id bind consumes the first prerequisite edit before any claim family closes.
- Role/state disclosure closes first at 8 cumulative edits, welfare decomposition closes at 18, and paired leaderboard interpretation closes at 29.
- The editable-surface, mutation-witness, and phase-3 world-emission claim families still stay citation-first after all seed-local fills because the engine-level world-aware rematching contract is not yet endogenous.

## Counts

- claim_family_count: 8
- safe_to_cite_now_count: 2
- native_stage_unlock_count: 3
- blocked_by_engine_gap_count: 3
- distinct_actionable_frontier_count: 3
- actionable_cumulative_frontier_sequence: 8, 18, 29
- benchmark_identity_prerequisite_edit_count: 1

## Frontier buckets

| frontier_kind | claim_family_count | claim_family_ids | summary |
|---|---:|---|---|
| `safe_to_cite_now` | 2 | `RWC-003`, `RWC-008` | These claim families already have enough compact evidence in the archive and do not wait on any remaining rematch-world open question or engine gap. |
| `native_stage_unlock` | 3 | `RWC-005`, `RWC-006`, `RWC-007` | These claim families become world-native safe only after the listed cumulative native-fill stages are complete; the benchmark-id bind is a prerequisite but closes no claim family by itself. |
| `blocked_by_engine_gap` | 3 | `RWC-001`, `RWC-002`, `RWC-004` | These claim families remain citation-first even after seed-local fills because they still depend on the unresolved cross-section engine contract `SG-003`. |

## Claim frontier matrix

| claim_family_id | frontier_kind | claim_label | frontier_or_blocker |
|---|---|---|---|
| `RWC-003` | `safe_to_cite_now` | landing order and closeout sequence | ready now |
| `RWC-008` | `safe_to_cite_now` | final package-boundary authority | ready now |
| `RWC-005` | `native_stage_unlock` | role and rematch-state disclosure | `8` edits via `world_semantics_contract` |
| `RWC-006` | `native_stage_unlock` | delay tax versus efficiency and welfare decomposition | `18` edits via `occupancy_accounting_contract` |
| `RWC-007` | `native_stage_unlock` | paired leaderboard interpretation | `29` edits via `paired_ranking_views_contract` |
| `RWC-001` | `blocked_by_engine_gap` | editable native-fill surface | `SG-003` |
| `RWC-002` | `blocked_by_engine_gap` | concrete mutation witness | `SG-003` |
| `RWC-004` | `blocked_by_engine_gap` | phase-3 world emission witness | `SG-003` |

## Claim family details

### RWC-003 — landing order and closeout sequence

- frontier_kind: `safe_to_cite_now`
- claim_summary: The publication floor resolves to 7 ordered edit stages and 5 ordered closeout phases rather than an ad hoc bundle/prune/package ritual.
- why_it_matters: Keeps the first native landing reproducible and small by turning procedure memory into one exact ordered witness.
- current_state: already safe to cite from retained compact surfaces
- minimal_citation_paths:
  - `docs/REMATCH_WORLD_BENCHMARK_LANDING_LADDER.md`
  - `docs/REMATCH_WORLD_BENCHMARK_CLOSEOUT_LIFECYCLE_LEDGER.md`
- open_spec_ids: none

### RWC-008 — final package-boundary authority

- frontier_kind: `safe_to_cite_now`
- claim_summary: Final authority is the post-prune -> chain -> package closeout path: the lifecycle ledger names the surviving authority sequence and the package receipt is already `package_ready=True` with 7/7 policy checks passed.
- why_it_matters: Prevents the archive from mistaking the pre-prune retention gate for final package authority when cutting a real publication zip.
- current_state: already safe to cite from retained compact surfaces
- minimal_citation_paths:
  - `docs/REMATCH_WORLD_BENCHMARK_CLOSEOUT_LIFECYCLE_LEDGER.md`
  - `examples/snapshots/rematch_world_benchmark_package_receipt.json`
- open_spec_ids: none

### RWC-005 — role and rematch-state disclosure

- frontier_kind: `native_stage_unlock`
- claim_summary: Role assignment and rematch-state carry are still provisional interpretation surfaces: the world card names the copied frozen semantics handoff, but asymmetry still requires explicit role policy and a companion role-swapped benchmark when material.
- why_it_matters: Warns inheritors not to oversell asymmetry-sensitive claims from the bridge benchmark before the open role/state question is resolved.
- cumulative_required_edit_count: 8
- frontier_stage: `world_semantics_contract` (fill world_semantics_contract)
- resolver_ids: `SQ-012`
- native_sections: `world_semantics_contract`
- blocking_slot_total: 6
- benchmark_identity_prerequisite_edit_count: 1
- frontier_dependency_reason: Define role assignment plus carry/reset semantics before attaching quantitative benchmark rows to one institution.
- minimal_citation_paths:
  - `docs/REMATCH_WORLD_BENCHMARK_WORLD_EMISSION_CARD.md`
- open_spec_ids: `SA-011`, `SQ-012`

### RWC-006 — delay tax versus efficiency and welfare decomposition

- frontier_kind: `native_stage_unlock`
- claim_summary: Delay-tax and welfare claims remain provisional until occupancy accounting is treated as non-optional: the bridge benchmark already exposes the relevant copied handoffs, but comparative welfare still depends on matched-vs-searching and occupancy decomposition fields.
- why_it_matters: Separates what the archive can already publish from the stronger market-efficiency and welfare claims that still need explicit world-native disclosure rules.
- cumulative_required_edit_count: 18
- frontier_stage: `occupancy_accounting_contract` (fill occupancy_accounting_contract)
- resolver_ids: `SQ-013`, `SQ-014`
- native_sections: `matching_state_contract`, `occupancy_accounting_contract`
- blocking_slot_total: 8
- benchmark_identity_prerequisite_edit_count: 1
- frontier_dependency_reason: Populate aggregate-versus-in-match welfare decomposition only after the matching-state terms are concrete.
- minimal_citation_paths:
  - `docs/REMATCH_WORLD_BENCHMARK_WORLD_EMISSION_CARD.md`
- open_spec_ids: `SA-012`, `SA-013`, `SQ-013`, `SQ-014`

### RWC-007 — paired leaderboard interpretation

- frontier_kind: `native_stage_unlock`
- claim_summary: Leaderboard claims are still provisional unless paired occupancy/tempo views remain visible: the native-fill map names the paired-ranking contract as one of the 5 native sections, but the archive still treats aggregate-only leaderboards as incomplete.
- why_it_matters: Keeps eventual rankings honest by requiring occupancy-normalized paired views rather than letting aggregate welfare hide tempo artifacts.
- cumulative_required_edit_count: 29
- frontier_stage: `paired_ranking_views_contract` (fill paired_ranking_views_contract)
- resolver_ids: `SQ-015`, `SQ-016`
- native_sections: `turnover_tempo_contract`, `paired_ranking_views_contract`
- blocking_slot_total: 9
- benchmark_identity_prerequisite_edit_count: 1
- frontier_dependency_reason: Publish aggregate-versus-in-match leaderboards only after the underlying payoff decomposition has been filled.
- minimal_citation_paths:
  - `docs/REMATCH_WORLD_BENCHMARK_WORLD_EMISSION_CARD.md`
  - `docs/REMATCH_WORLD_BENCHMARK_NATIVE_FILL_MAP.md`
- open_spec_ids: `SA-015`, `SQ-015`, `SQ-016`

### RWC-001 — editable native-fill surface

- frontier_kind: `blocked_by_engine_gap`
- claim_summary: The first native rematch-world publication is already narrowed to 5 native sections with 24 exact blocker loci, while 8 copied sections stay frozen and citation-first.
- why_it_matters: Lets the first Rust-capable inheritor start from one exact edit boundary instead of rediscovering where native work is allowed.
- blocking_resolver_id: `SG-003`
- blocking_resolver_summary: The engine-level contract for endogenous rematching and world-aware strategy canonicalization is underspecified.
- current_bridge_paths:
  - `docs/REMATCH_WORLD_BENCHMARK_EXAMPLE_DELTA_LEDGER.md`
  - `docs/REMATCH_WORLD_BENCHMARK_NATIVE_FILL_MAP.md`
  - `docs/REMATCH_WORLD_BENCHMARK_WORLD_EMISSION_CARD.md`
  - `examples/snapshots/rematch_world_benchmark_publication_bundle_receipt.json`
- open_spec_ids: `SG-003`

### RWC-002 — concrete mutation witness

- frontier_kind: `blocked_by_engine_gap`
- claim_summary: The synthetic compiled example changes exactly 33 JSON paths: 30 required publication-floor changes plus 3 optional row insertions inside already-allowed prefixes.
- why_it_matters: Gives the implementor one exact mutation witness for the first landing without reopening both the seed and compiled artifact.
- blocking_resolver_id: `SG-003`
- blocking_resolver_summary: The engine-level contract for endogenous rematching and world-aware strategy canonicalization is underspecified.
- current_bridge_paths:
  - `docs/REMATCH_WORLD_BENCHMARK_EXAMPLE_DELTA_LEDGER.md`
  - `docs/REMATCH_WORLD_BENCHMARK_NATIVE_FILL_MAP.md`
  - `docs/REMATCH_WORLD_BENCHMARK_WORLD_EMISSION_CARD.md`
  - `examples/snapshots/rematch_world_benchmark_publication_bundle_receipt.json`
- open_spec_ids: `SG-003`

### RWC-004 — phase-3 world emission witness

- frontier_kind: `blocked_by_engine_gap`
- claim_summary: The retained bundle receipt already proves `world_emission_ready=True` across 10 emitted question ids while keeping the compiled patch scratch-only.
- why_it_matters: Preserves one compact proof that the benchmark really emits the copied phase-3 decision contract even before a world-native contract exists.
- blocking_resolver_id: `SG-003`
- blocking_resolver_summary: The engine-level contract for endogenous rematching and world-aware strategy canonicalization is underspecified.
- current_bridge_paths:
  - `docs/REMATCH_WORLD_BENCHMARK_EXAMPLE_DELTA_LEDGER.md`
  - `docs/REMATCH_WORLD_BENCHMARK_NATIVE_FILL_MAP.md`
  - `docs/REMATCH_WORLD_BENCHMARK_WORLD_EMISSION_CARD.md`
  - `examples/snapshots/rematch_world_benchmark_publication_bundle_receipt.json`
- open_spec_ids: `SA-003`, `SG-003`

## Recommended next move

- Use this frontier before filling or citing the benchmark: close native claim families in 8 -> 18 -> 29 cumulative-edit order, and keep the SG-003 families citation-first until the engine contract itself exists.
