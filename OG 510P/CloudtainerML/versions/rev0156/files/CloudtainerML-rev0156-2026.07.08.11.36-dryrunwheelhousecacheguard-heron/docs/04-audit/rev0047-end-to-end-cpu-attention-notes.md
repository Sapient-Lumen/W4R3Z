# rev0047 end-to-end CPU attention notes

This revision closes the most immediate timing gap left by rev0046. The prior native timing artifact measured selector work only. rev0047 adds a C++ single-row attention benchmark that times QK score computation, selector work, sparse or dense softmax, and value accumulation in one forward path.

The benchmark is intentionally scoped as native CPU row attention, not as a fused GPU kernel or model-throughput claim.

## Main result

The frontier is mixed and useful:

- Exact Top-K-32 is fast but fails the attention-output quality bar across the tested regimes.
- Mass histogram selection is a real sparse win on the peaked bounded regime: it reads roughly 5% of values and is faster than dense, though it misses the strict quality bar on some rows.
- Broad bounded attention collapses the mass histogram to dense-width reads, making it slower than dense.
- Value-norm exception repair fixes the high-norm tail regime, but the metadata scan and exception scheduling make it slower than dense on this CPU implementation.

## Interpretation

This is forward progress because timing now includes the expensive parts selector-only timing omitted. It is also a veto: quality-preserving sparse attention is regime-dependent, and safety guards can erase CPU speedups.

Promotion remains blocked pending public/pretrained attention traces and GPU or accelerator fused-kernel timing.
