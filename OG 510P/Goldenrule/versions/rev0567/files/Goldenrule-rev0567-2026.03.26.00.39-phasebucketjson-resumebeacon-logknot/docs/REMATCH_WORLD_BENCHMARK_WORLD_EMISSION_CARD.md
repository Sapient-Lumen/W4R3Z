# Rematch-world benchmark world-emission card

Focus: collapse the first endogenous rematch-world benchmark fill, copy-forward, phase-3 emission, prune, and package discipline into one inheritor-facing control surface

## Local result

- The standing seed still expects exactly `5` native fills: `world_semantics_contract`, `matching_state_contract`, `occupancy_accounting_contract`, `turnover_tempo_contract`, `paired_ranking_views_contract`.
- The copied contract surface stays frozen across `8` sections while the mutation guard still allows only `12` mutable prefixes against `26` frozen prefixes.
- The retained publication bundle already proves `world_emission_ready=true` and emits `10` phase-3 question ids across `delay_contract`, `winner_contract`, and `delta_contract`.
- The durable publication set is `6` objects / `93320` bytes; the explicit transient exit set is `4` objects / `3728` bytes.
- Important sequencing nuance: the example retention gate still says `retention_exit_ready=false`, but the cleaned-tree authority already lands later at `overall_chain_ready=true` and `package_ready=true` once post-prune/package receipts are in hand.

## Native fill targets

| order | section | linked questions | status |
|---|---|---|---|
| 1 | `world_semantics_contract` | SQ-012 | `pending_fill` |
| 2 | `matching_state_contract` | SQ-013 | `pending_fill` |
| 3 | `occupancy_accounting_contract` | SQ-014 | `pending_fill` |
| 4 | `turnover_tempo_contract` | SQ-015 | `pending_fill` |
| 5 | `paired_ranking_views_contract` | SQ-016 | `pending_fill` |

## Frozen copied surface that should stay citation-first

| section | linked questions | source |
|---|---|---|
| `canonicalization_planner_contract` | SQ-003, SQ-004, SQ-005, SQ-006, SQ-007, SQ-008, SQ-009, SQ-010, SQ-011 | `examples/snapshots/rematch_world_benchmark_canonicalization_handoff.json` |
| `winner_triage_handoff` | SQ-018, SQ-019, SQ-020, SQ-021 | `examples/snapshots/rematch_world_benchmark_winner_triage_handoff.json` |
| `delta_shortlist_handoff` | SQ-022 | `examples/snapshots/rematch_world_benchmark_delta_shortlist_handoff.json` |
| `paired_ranking_interpretation_handoff` | SQ-014, SQ-016 | `examples/snapshots/rematch_world_benchmark_paired_ranking_interpretation_handoff.json` |
| `matching_state_interpretation_handoff` | SQ-013 | `examples/snapshots/rematch_world_benchmark_matching_state_interpretation_handoff.json` |
| `turnover_tempo_interpretation_handoff` | SQ-015 | `examples/snapshots/rematch_world_benchmark_turnover_tempo_interpretation_handoff.json` |
| `world_semantics_interpretation_handoff` | SQ-012 | `examples/snapshots/rematch_world_benchmark_world_semantics_interpretation_handoff.json` |
| `compact_decision_bundle` | SQ-017, SQ-018, SQ-019, SQ-020, SQ-021, SQ-022, SQ-023, SQ-024, SQ-025, SQ-026 | `artifacts/reports/rematch_decision_contract_snapshot_20260316.json` |

## Landing ladder

| step | stage | tool | success witness | receipt |
|---|---|---|---|---|
| 1 | freeze copied seed surface | `scripts/tools/audit_rematch_world_benchmark_frozen_handoffs.py` | exact_match_count=8 across 8 copied sections | `examples/snapshots/rematch_world_benchmark_frozen_handoff_audit_receipt.json` |
| 2 | retain tiny provenance for distilled run facts | `scripts/tools/build_rematch_world_benchmark_evidence_receipt.py` | strict_coverage_passed=true with scratch_source_count=3 | `examples/snapshots/rematch_world_benchmark_evidence_receipt.json` |
| 3 | compile back and preflight the filled artifact | `scripts/tools/rematch_world_benchmark_publication_preflight.py` | preflight_ready=true, mutation_surface_ok=true, completion_ready=true, filled_world_section_count=5 | `examples/snapshots/rematch_world_benchmark_preflight_receipt.json` |
| 4 | prove copied handoffs survived compilation unchanged | `scripts/tools/audit_rematch_world_benchmark_copy_forward.py` | exact_match_count=8 and mismatch_count=0 | `examples/snapshots/rematch_world_benchmark_copy_forward_audit_receipt.json` |
| 5 | bundle one compact phase-3 emission proof | `scripts/tools/build_rematch_world_benchmark_publication_bundle_receipt.py` | patch_elision_ready=true, world_emission_ready=true, emitted_question_id_count=10 | `examples/snapshots/rematch_world_benchmark_publication_bundle_receipt.json` |
| 6 | audit the retained publication spine | `scripts/tools/audit_rematch_world_benchmark_publication_spine.py` | publication_spine_ready=true with durable_spine_bytes=86287 | `examples/snapshots/rematch_world_benchmark_publication_spine_audit_receipt.json` |
| 7 | decide whether intermediates may exit | `scripts/tools/build_rematch_world_benchmark_retention_exit_receipt.py` | retention_exit_ready=false (this is a gate, not the final zip authority) | `examples/snapshots/rematch_world_benchmark_retention_exit_receipt.json` |
| 8 | prune exit-ready transients by rule | `scripts/tools/prune_rematch_world_benchmark_transients.py --execute` | prune_ready=true, deleted_count=1, already_absent_count=3 | `examples/snapshots/rematch_world_benchmark_prune_execute_receipt.json` |
| 9 | prove cleaned tree zip-readiness | `scripts/tools/audit_rematch_world_benchmark_post_prune_state.py` | cleaned_tree_ready_for_zip=true with transient_still_present_count=0 | `examples/snapshots/rematch_world_benchmark_post_prune_audit_receipt.json` |
| 10 | emit inheritor-facing chain and package proofs | `scripts/tools/build_rematch_world_benchmark_publication_chain_receipt.py + scripts/tools/build_rematch_world_benchmark_package_receipt.py` | overall_chain_ready=true, package_ready=true | `examples/snapshots/rematch_world_benchmark_publication_chain_receipt.json ; examples/snapshots/rematch_world_benchmark_package_receipt.json` |

## Durable publication objects after successful closeout

| label | bytes | path |
|---|---|---|
| `evidence_packet` | 3103 | `examples/snapshots/rematch_world_benchmark_evidence_packet.json` |
| `evidence_receipt` | 1904 | `examples/snapshots/rematch_world_benchmark_evidence_receipt.json` |
| `compiled_benchmark_artifact` | 79229 | `examples/snapshots/rematch_world_benchmark_compiled_artifact.json` |
| `preflight_receipt` | 2051 | `examples/snapshots/rematch_world_benchmark_preflight_receipt.json` |
| `publication_bundle_receipt` | 3904 | `examples/snapshots/rematch_world_benchmark_publication_bundle_receipt.json` |
| `publication_spine_audit_receipt` | 3129 | `examples/snapshots/rematch_world_benchmark_publication_spine_audit_receipt.json` |

## Package hygiene checks

- `compiled_artifact_digest_consistent` = `true`
- `pdf_free_tree` = `true`
- `post_prune_zip_ready` = `true`
- `publication_chain_ready` = `true`
- `pycache_free_tree` = `true`
- `scratch_manifest_clear` = `true`
- `scratch_tree_empty` = `true`

## Implementor takeaway

On the first real endogenous rematch-world run, fill only the five pending native sections, keep the eight copied sections frozen, and treat the authoritative publication closeout as bundle -> spine audit -> post-prune audit -> chain receipt -> package receipt rather than as the pre-prune retention gate alone.
