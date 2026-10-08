# Rematch-world benchmark landing ladder

Focus: collapse the first native rematch-world publication into one exact edit ladder plus one exact closeout ladder so the next implementor can land the benchmark without reopening scattered receipts

## Local result
- The minimum publishable native-fill path is an exact 7-stage edit ladder ending at 30 required edits with cumulative checkpoints 1, 8, 12, 18, 23, 29, 30.
- The only blocking metadata mutation is `benchmark_id`; every other required edit belongs to one of the five native world sections, and `artifact_state` flips only after those blockers are gone.
- The section order is not arbitrary: define institution semantics first, then define matching/dead-time semantics, then publish occupancy and turnover telemetry, and only then publish paired ranking views.
- After the edit ladder, the closeout path compresses to five proof phases: seed guards, filled-artifact validation, retained emission proof, transient exit/prune, and final chain/package authority.

## Exact edit ladder

| order | stage | required edits | cumulative | blocker clears | status flips | prefixes | why this order |
|---|---|---:|---:|---:|---:|---|---|
| 1 | bind benchmark identity | `1` | `1` | `1` | `0` | `benchmark_id` | Anchor the retained artifact to one concrete benchmark id before publishing native rows or package receipts against it. |
| 2 | fill world_semantics_contract | `7` | `8` | `6` | `1` | `world_semantics_contract`, `section_status.world_semantics_contract` | Define role assignment plus carry/reset semantics before attaching quantitative benchmark rows to one institution. |
| 3 | fill matching_state_contract | `4` | `12` | `3` | `1` | `matching_state_contract`, `section_status.matching_state_contract` | Declare rematch delay versus matching-efficiency semantics before any dead-round or turnover comparison is interpreted. |
| 4 | fill occupancy_accounting_contract | `6` | `18` | `5` | `1` | `occupancy_accounting_contract.policy_rows`, `section_status.occupancy_accounting_contract` | Populate aggregate-versus-in-match welfare decomposition only after the matching-state terms are concrete. |
| 5 | fill turnover_tempo_contract | `5` | `23` | `4` | `1` | `turnover_tempo_contract.policy_rows`, `section_status.turnover_tempo_contract` | Bind turnover metrics after the matching-state semantics and occupancy decomposition are already fixed. |
| 6 | fill paired_ranking_views_contract | `6` | `29` | `5` | `1` | `paired_ranking_views_contract.leaderboard_rows`, `section_status.paired_ranking_views_contract` | Publish aggregate-versus-in-match leaderboards only after the underlying payoff decomposition has been filled. |
| 7 | flip artifact state | `1` | `30` | `0` | `0` | `artifact_state` | Only mark the artifact `filled_benchmark` after every blocking native locus has been replaced with concrete content. |

## Post-edit closeout ladder

| order | phase | landing steps | receipts | why now |
|---|---|---|---|---|
| 1 | seed guards | `1, 2` | `examples/snapshots/rematch_world_benchmark_frozen_handoff_audit_receipt.json`; `examples/snapshots/rematch_world_benchmark_evidence_receipt.json` | Prove the copied surface is still frozen and retain only tiny provenance before compiling a filled artifact. |
| 2 | filled artifact validation | `3, 4` | `examples/snapshots/rematch_world_benchmark_preflight_receipt.json`; `examples/snapshots/rematch_world_benchmark_copy_forward_audit_receipt.json` | Compile the in-place fill, run the mutation/completion gates, and prove the copied handoffs survived unchanged. |
| 3 | retained emission proof | `5, 6` | `examples/snapshots/rematch_world_benchmark_publication_bundle_receipt.json`; `examples/snapshots/rematch_world_benchmark_publication_spine_audit_receipt.json` | Collapse the phase-3 benchmark emission into one compact retained bundle and then audit the durable publication spine. |
| 4 | transient exit and prune | `7, 8, 9` | `examples/snapshots/rematch_world_benchmark_retention_exit_receipt.json`; `examples/snapshots/rematch_world_benchmark_prune_execute_receipt.json`; `examples/snapshots/rematch_world_benchmark_post_prune_audit_receipt.json` | Decide which intermediates may exit, prune them by rule, and prove the cleaned tree is actually zip-ready. |
| 5 | final authority receipts | `10` | `examples/snapshots/rematch_world_benchmark_publication_chain_receipt.json ; examples/snapshots/rematch_world_benchmark_package_receipt.json` | Emit the inheritor-facing chain and package proofs only after the post-prune tree is already known good. |

## Implementor takeaway

Replay the 7-stage edit ladder to reach the 30-edit publication floor, then walk the 5-phase closeout ladder in order instead of improvising receipts or retaining extra scratch.

