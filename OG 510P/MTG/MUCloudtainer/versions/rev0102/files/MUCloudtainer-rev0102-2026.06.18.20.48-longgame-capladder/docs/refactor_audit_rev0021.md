# rev0021 refactor/audit notes

## Refactor

`src/muc5/cpp_trace.py` now separates trace preparation from C++ finalization:

```text
PreparedCppTraceBatch
prepare_public_traces_for_cpp
finalize_cpp_trace_batch
check_public_traces_with_cpp
```

The old `check_public_traces_with_cpp(...)` API remains intact, but internally it now uses the two-phase seam.  This makes benchmarks and future batch rollout experiments less likely to duplicate semantic replay logic.

## New audit targets

rev0021 audit checks:

- C++ batch benchmark exists and reports zero mismatches.
- Prepared trace support remains complete on the rev0020 trace corpus.
- Batched C++ calls are measured separately from Python trace preparation.
- The frozen ranker model exists and can be loaded through the public-agent factory.
- The ranker imitation smoke score beats the random-slot baseline.
- The ranker payoff table passes promotion and statistical gates.
- Replay samples for ranker policy evaluation pass.

## C++ policy

The archive remains cloudtainer-bound:

```text
Python = semantic reference / audit shell / analytics
C++    = stable hot kernels / batch execution / future rollout core
```

The C++ migration priority after rev0021 is no longer merely "cover more transitions."  It is now:

```text
use batched C++ seams wherever possible
  -> avoid subprocess-per-action overhead
  -> keep Python replay/fingerprint gates around every C++ result
```
