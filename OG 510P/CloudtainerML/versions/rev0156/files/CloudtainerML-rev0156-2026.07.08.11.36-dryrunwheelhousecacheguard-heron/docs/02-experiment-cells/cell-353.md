# CELL-353 — Blockwise GQA Index Branch Wind Tunnel

Priority: **P0**  
Status: native-probe-added

## Question

When does a MiniMax/MSA-style per-GQA-group block index branch beat dense, local-only, and shared-index sparse attention under exactness and selector-cost guards?

## Cheap first run

Compile/run experiments/blockwise_index_branch/blockwise_index_branch.cpp. Sweep local, boundary, far-needle, group-specific, off-phase, distractor, and smooth regimes.

## Metrics

- `score`
- `target_miss`
- `recall`
- `block_cost`
- `selector_cost`
- `wall_proxy`
- `false_blocks`
- `local_anchor`
- `bridge_anchor`
- `regret`

## Required baselines

- `dense_full`
- `local_block_only`
- `shared_block_index_once`
- `msa_group_block_index`
- `msa_plus_boundary_anchor`
- `token_oracle_upper`

## Stop condition

Promote block index branches only if they beat shared/local baselines under exactness, selector-cost, and false-block traffic guards.
