# CELL-274 — Sparse Frontier IsoFLOPS Phase Diagram

- priority: P0
- status: implemented-native-rev0025
- idea: IDEA-0273
- sources: SRC-0296

## Cheap first run

Compare dense/sparse/hybrid models at soft equal compute across task and prefill/decode phase.

## Metrics

- quality
- realized_cost
- regret
- score

## Required baselines

- small_dense
- medium_dense
- large_block_sparse
- large_token_sparse
- large_adaptive_sparse
- oracle_sparse

## Stop condition

Promote if sparse larger models win some regimes and lose others for understandable reasons.
