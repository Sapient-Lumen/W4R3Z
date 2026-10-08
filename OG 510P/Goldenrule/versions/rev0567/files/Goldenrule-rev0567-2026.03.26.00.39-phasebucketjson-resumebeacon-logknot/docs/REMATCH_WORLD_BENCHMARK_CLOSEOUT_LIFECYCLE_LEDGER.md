# Rematch-world benchmark closeout lifecycle ledger

Focus: collapse the rematch-world publication closeout into one exact lifecycle ledger so inheritors can see what must persist, what may exit, and which receipts are actual final authority without reopening seven separate receipts

## Local result
- The durable publication set is exactly 6 objects / 93320 bytes, while the whole closeout proof family adds only 7 compact retained receipts / 32301 bytes.
- The transient exit surface stays tiny and explicit: 4 rows / 3728 bytes, with only 1 concrete deletion and 3 already-absent scratch rows in the standing example.
- The retention-exit receipt is intentionally not the final authority surface: it can remain `retention_exit_ready=false` even when the real closeout succeeds later at post-prune zip readiness, publication-chain readiness, and package readiness.
- After closeout, the synthetic rematch-world publication path retains 13 exact objects / 125621 bytes across the durable publication set plus the surviving proof receipts, without keeping the compiled fill patch or scratch source files.

## Lifecycle counts

| category | count | bytes | note |
|---|---:|---:|---|
| durable publication set | `6` | `93320` | exact objects that remain reconstructible without the fill patch |
| closeout proof receipts | `7` | `32301` | guard / cleanup / authority receipts retained around the durable spine |
| transient exit surface | `4` | `3728` | explicit patch/scratch rows allowed to leave after proof succeeds |
| final retained closeout set | `13` | `125621` | durable publication set plus surviving proof receipts |

## Durable publication set

| label | bytes | path |
|---|---:|---|
| `evidence_packet` | `3103` | `examples/snapshots/rematch_world_benchmark_evidence_packet.json` |
| `evidence_receipt` | `1904` | `examples/snapshots/rematch_world_benchmark_evidence_receipt.json` |
| `compiled_benchmark_artifact` | `79229` | `examples/snapshots/rematch_world_benchmark_compiled_artifact.json` |
| `preflight_receipt` | `2051` | `examples/snapshots/rematch_world_benchmark_preflight_receipt.json` |
| `publication_bundle_receipt` | `3904` | `examples/snapshots/rematch_world_benchmark_publication_bundle_receipt.json` |
| `publication_spine_audit_receipt` | `3129` | `examples/snapshots/rematch_world_benchmark_publication_spine_audit_receipt.json` |

## Exit-ready transient surface

| label | bytes | final status | path |
|---|---:|---|---|
| `compiled_fill_patch` | `3176` | `confirmed_absent_after_prune` | `examples/scratch/rematch_world_benchmark/compiled_fill_patch.json` |
| `scratch_source:world_semantics_notes` | `264` | `confirmed_absent_after_prune` | `examples/scratch/rematch_world_benchmark/source_world_semantics.json` |
| `scratch_source:policy_metrics_table` | `214` | `confirmed_absent_after_prune` | `examples/scratch/rematch_world_benchmark/source_policy_metrics.tsv` |
| `scratch_source:leaderboard_table` | `74` | `confirmed_absent_after_prune` | `examples/scratch/rematch_world_benchmark/source_leaderboard.csv` |

## Closeout proof receipts

| label | phase | role | ready | bytes | path |
|---|---|---|---|---:|---|
| `frozen_handoff_audit_receipt` | `seed_guards` | `upstream_guard` | `true` | `5887` | `examples/snapshots/rematch_world_benchmark_frozen_handoff_audit_receipt.json` |
| `copy_forward_audit_receipt` | `filled_artifact_validation` | `upstream_guard` | `true` | `5559` | `examples/snapshots/rematch_world_benchmark_copy_forward_audit_receipt.json` |
| `retention_exit_receipt` | `transient_exit_and_prune` | `pre_prune_gate_only` | `false` | `4973` | `examples/snapshots/rematch_world_benchmark_retention_exit_receipt.json` |
| `prune_execute_receipt` | `transient_exit_and_prune` | `cleanup_execution` | `true` | `3117` | `examples/snapshots/rematch_world_benchmark_prune_execute_receipt.json` |
| `post_prune_audit_receipt` | `transient_exit_and_prune` | `zip_readiness_input` | `true` | `5566` | `examples/snapshots/rematch_world_benchmark_post_prune_audit_receipt.json` |
| `publication_chain_receipt` | `final_authority_receipts` | `inheritor_facing_chain_authority` | `true` | `3365` | `examples/snapshots/rematch_world_benchmark_publication_chain_receipt.json` |
| `package_receipt` | `final_authority_receipts` | `package_boundary_authority` | `true` | `3834` | `examples/snapshots/rematch_world_benchmark_package_receipt.json` |

## Exact lifecycle ledger

| label | class | phase | final status | bytes | status summary |
|---|---|---|---|---:|---|
| `evidence_packet` | `durable_retained_object` | `retained_emission_proof` | `retained_after_closeout` | `3103` | retained as part of the durable publication set |
| `evidence_receipt` | `durable_retained_object` | `retained_emission_proof` | `retained_after_closeout` | `1904` | retained as part of the durable publication set |
| `compiled_benchmark_artifact` | `durable_retained_object` | `retained_emission_proof` | `retained_after_closeout` | `79229` | retained as part of the durable publication set |
| `preflight_receipt` | `durable_retained_object` | `retained_emission_proof` | `retained_after_closeout` | `2051` | retained as part of the durable publication set |
| `publication_bundle_receipt` | `durable_retained_object` | `retained_emission_proof` | `retained_after_closeout` | `3904` | retained as part of the durable publication set |
| `publication_spine_audit_receipt` | `durable_retained_object` | `retained_emission_proof` | `retained_after_closeout` | `3129` | retained as part of the durable publication set |
| `compiled_fill_patch` | `exit_ready_transient_object` | `transient_exit_and_prune` | `confirmed_absent_after_prune` | `3176` | prune_status=deleted; confirmed_absent=True |
| `scratch_source:world_semantics_notes` | `exit_ready_transient_object` | `transient_exit_and_prune` | `confirmed_absent_after_prune` | `264` | prune_status=already_absent; confirmed_absent=True |
| `scratch_source:policy_metrics_table` | `exit_ready_transient_object` | `transient_exit_and_prune` | `confirmed_absent_after_prune` | `214` | prune_status=already_absent; confirmed_absent=True |
| `scratch_source:leaderboard_table` | `exit_ready_transient_object` | `transient_exit_and_prune` | `confirmed_absent_after_prune` | `74` | prune_status=already_absent; confirmed_absent=True |
| `frozen_handoff_audit_receipt` | `guard_proof_receipt` | `seed_guards` | `retained_after_closeout` | `5887` | Standing seed rebuild-matches and all copied frozen sections hash-match their standalone sources. |
| `copy_forward_audit_receipt` | `guard_proof_receipt` | `filled_artifact_validation` | `retained_after_closeout` | `5559` | Compiled benchmark artifact preserved all copied frozen sections and the compact decision bundle unchanged. |
| `retention_exit_receipt` | `cleanup_gate_receipt` | `transient_exit_and_prune` | `retained_after_closeout` | `4973` | retention_exit_ready=false until scratch hashes are re-proved on the current tree; this is a gate, not final package authority |
| `prune_execute_receipt` | `cleanup_action_receipt` | `transient_exit_and_prune` | `retained_after_closeout` | `3117` | deleted_count=1, already_absent_count=3, removed_bytes=3176 |
| `post_prune_audit_receipt` | `zip_readiness_receipt` | `transient_exit_and_prune` | `retained_after_closeout` | `5566` | Durable publication spine still hash-matches after cleanup and exit-ready transients are absent or unlinked. |
| `publication_chain_receipt` | `final_authority_receipt` | `final_authority_receipts` | `retained_after_closeout` | `3365` | overall_chain_ready=True across 4/4 links |
| `package_receipt` | `final_authority_receipt` | `final_authority_receipts` | `retained_after_closeout` | `3834` | package_ready=True with 7/7 policy checks passed |

## Implementor takeaway

Use this ledger when cutting the first real native publication: keep the six-object durable publication set plus the compact proof receipts, let the explicit transient rows exit by rule, and treat final authority as post-prune audit -> publication-chain receipt -> package receipt rather than as the retention-exit gate alone.

