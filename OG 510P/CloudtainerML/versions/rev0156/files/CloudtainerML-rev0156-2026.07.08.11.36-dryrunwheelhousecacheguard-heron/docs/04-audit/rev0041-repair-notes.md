# Repair notes — rev0041

## What changed

This revision focuses on the riskiest unfinished work from rev0040: invalid comparison surfaces that could mislead future decisions.

### 1. GVR temporal Top-K was de-oracled

The old toy asked whether true current Top-K indices were inside the GVR candidate set and used that hidden oracle to decide fallback. The repaired source no longer passes current truth into the selector. Candidate containment is certified only from scanned scores: after threshold collection and candidate refinement, the selected kth score must be at least the maximum omitted score. If the candidate set underflows, overflows the buffer cap, or cannot certify, the method pays an explicit heap-exact fallback.

Fresh artifact: `artifacts/probe-results/REV0041_GVR_TOPK_TEMPORAL_DEORACLE_SMOKE.json`.

Key result: `gvr_certified_cap6` is exact on all 600 rows, wins 261 rows, and falls back 198 times. `exact_heap_baseline` wins 177 rows. This is a much less glamorous but more honest result: GVR has a regime-dependent candidate/fallback tradeoff rather than free exactness.

### 2. Gate compiler validation was made real

The old `validation_topk_budget` branch was identical to `topk_budget3`. The repaired source removes that alias. `validation_selected` now chooses among threshold, Top-K, knee, uncertainty-band, and cost-capped compilers on held-out calibration rows, then applies the chosen policy to test rows.

Fresh artifact: `artifacts/probe-results/REV0041_GATE_COMPILER_FRONTIER_REPAIR_SMOKE.json`.

Key result: `validation_selected` has mean score 1.349978 and only 4 exact misses, while simple policies have larger regret in several regimes. This is still synthetic compiler-choice evidence, not model evidence.

### 3. A canonical compiler benchmark now exists

Fresh artifact: `artifacts/probe-results/REV0041_CANONICAL_SPARSE_COMPILER_BENCHMARK.json`.

One score stream now feeds exact heap, threshold, Top-p, hybrid threshold/Top-K, block-index certification, and temporal GVR. Temporal GVR wins 306 of 600 rows with 33.3% fallback; exact heap wins 294 rows. Block index certifies only by falling back on this generator, which is a useful negative signal.

## What did not change

- The bridge annealing lane is still negative/mislabeled until temperature or hard sampling is in the forward path.
- The block-index lane is still symbolic until the selector uses observable features and the attention/output/timing path is measured.
- Cost remains proxy cost. The next revision should measure wall time and memory traffic.
