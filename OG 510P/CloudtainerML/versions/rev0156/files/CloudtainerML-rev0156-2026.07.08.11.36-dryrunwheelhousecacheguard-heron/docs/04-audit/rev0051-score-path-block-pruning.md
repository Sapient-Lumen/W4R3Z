# rev0051 score-path block pruning notes

## Problem attacked

The previous attention line increasingly measured selected value reads and sidecar metadata cost, but a large claim risk remained: many selectors start from a full row of QK scores. That means they may be sparse only after dense score computation has already been paid.

## Change made

rev0051 adds `experiments/score_path_block_pruning/score_path_block_pruning.cpp`, a native CPU single-row benchmark with three paths:

1. dense full attention;
2. mass-histogram sparse attention after dense QK scoring;
3. block-upper-bound pruning using centroid/radius bounds to avoid exact token score computation for unopened blocks.

The block path certifies retained mass conservatively: unopened blocks contribute an upper bound to the denominator, while opened blocks use exact scores. It selects all opened tokens and stops only when the lower-bound mass certificate reaches 0.95.

## Main result

The dense-score histogram method is now explicitly claim-bounded. It can save value reads, but `qk_dot_fraction_vs_dense` remains 1.0 in every regime.

The block-bound path demonstrates the possible score-sparse route in `clustered_peaked_tight_bounds`: it uses a small fraction of dense token-score work and is a CPU speed win. But broad or loose-bound regimes collapse toward dense score work and are slower than dense on this CPU path.

## Audit/refactor

`tools/score_path_block_pruning_audit.py` checks:

- histogram selectors declare dense-score dependence;
- block-bound rows do not require exact dense scores;
- no selector reads values or dense outputs;
- tight clustered rows actually skip QK work;
- broad and loose-bound rows expose the near-dense collapse.

## Still blocked

- public/pretrained Q/K/V traces must be used to measure real block-bound tightness;
- GPU/fused kernel timing is still missing;
- current block geometry is synthetic and should not be promoted as model evidence.
