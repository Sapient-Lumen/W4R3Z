# rev0045 mass-certified compiler notes

This revision attacks the riskiest remaining scientific gap after the attention-output veto: a selector that preserves attention mass without using value vectors or dense attention outputs as an oracle.

## Change

`experiments/attention_compiler_core/attention_core.py` now contains score-only selection helpers:

- `delta_grid_mass_selection`: keep scores within a calibrated distance of the row maximum and certify mass from scores.
- `histogram_mass_selection`: bucket scores by distance from max, choose a cutoff bucket by score-only softmax mass, then gather values only for selected tokens.
- `block_local_topb_mass_selection`: widen top-b per block until score-only mass reaches target.

The new benchmark is `experiments/mass_certified_attention_compiler/mass_certified_attention_compiler.py` and emits `REV0045_MASS_CERTIFIED_ATTENTION_COMPILER.json`.

## Main result

On tiny trained-transformer traces, exact Top-K-8 selected 8/64 values but passed the quality bar only about 22.3% of rows. The sort-free histogram mass selector selected about 34.2/64 values, retained about 0.980 mass, and passed about 99.7% of rows. The delta grid was similar at about 34.8/64 values and 99.6% pass rate.

On broad synthetic attention rows, the result is less flattering: histogram selection still kept about 830.7/1024 values. That is honest forward progress: the compiler is valid, but broad-attention regimes are still not sparse wins.

## Scientific interpretation

The cube now has a candidate between exact small Top-K and oracle ordered Top-p. It is deployable in the sense that selection uses scores only, not V vectors or dense outputs, and it counts value reads after selection. It is not yet deployable in the systems sense: there is no named-hardware kernel, no public/pretrained trace, and no cache-aware gather implementation.
