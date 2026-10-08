# compat_layer_skips_local_benchmark_semantics

A crate reuses an existing local benchmark suite under a hosted CI compatibility layer.
The compatibility layer keeps the suite runnable, but some local semantics are not supported (for example Criterion `iter_custom` / `with_filter` or Divan `bench_group`).

The fixture exists to force the pack to record:

- that “the suite still runs” is not the same claim as “all benchmark semantics were preserved”,
- that compatibility-layer limitations belong in the environment-fidelity receipt,
- and that CI evidence imported through adapters may need a weaker trust class or a manual-review boundary.

Expected artifact pressure:
- `environment-fidelity.receipt` should classify the imported run as `compat_layer_limitation` when unsupported features are present.
- `noise-class.report` should not silently inherit the stronger local trust class.
- `perf-diff` should make support-gap changes loud across releases.
