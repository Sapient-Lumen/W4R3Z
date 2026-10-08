# rev0050 value-norm sidecar claim gate

rev0050 attacks the value-norm metadata assumption left open by rev0046–rev0049.

The previous result showed that high-norm, low-probability values can break mass-only sparse attention and that a value-norm exception selector can repair the constructed failure. What remained unsafe was the implicit assumption that value norms are free. rev0050 splits that path:

- `value_norm_exception_sidecar_0p95_sparse`: reads a precomputed value-norm sidecar and does not read V vectors during selection.
- `value_norm_exception_onthefly_0p95_sparse`: computes norms from V on the query path and is therefore a negative control, because it reads all values during selection.

The native CPU benchmark also refactors the certificate update. The old diagnostic recomputed the value-norm bound by rescanning all tokens after each exception. rev0050 keeps aggregate mass and weighted-norm terms live and updates them incrementally. This preserves the certificate semantics while removing an avoidable `O(N * exceptions)` waste path.

## Result

The sidecar path repairs the adversarial tail-quality failure without V/dense-output oracle leakage. However, in the current native CPU row-attention implementation it is **not a speed win**. It is a feasibility/claim-boundary step, not a promotion step.

The remaining blockers are:

1. actual public/pretrained attention traces;
2. GPU/fused attention-kernel timing;
3. a GPU/accelerator sidecar metadata path with bandwidth and scheduling accounted for.
