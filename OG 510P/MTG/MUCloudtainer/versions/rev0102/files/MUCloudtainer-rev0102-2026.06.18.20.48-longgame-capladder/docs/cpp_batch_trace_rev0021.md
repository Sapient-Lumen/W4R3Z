# rev0021 — C++ batch trace seam

rev0021 refactors the C++ recorded-trace checker into two explicit phases:

```text
prepare_public_traces_for_cpp(...)
  Python authoritative replay
  fingerprint/legal-menu checks
  one-action TransitionMicroRecord projection

finalize_cpp_trace_batch(...)
  one batched C++ executable call
  SIGv2 comparison
  summary/row labeling
```

The point is not only speed.  It is a cleaner trust contract.  Python still owns the rules, hidden information, replay fingerprints, and random-outcome transport.  C++ receives only flat transition records and must produce the same SIGv2 post-state signatures.

This matters for the long-haul C++ migration: a future full or partial C++ rollout core should be assembled from seams that have already survived directed tests, sampled gameplay, and recorded traces.  A fast C++ engine that is not semantically pinned to Python would poison every downstream learning result.

The benchmark script is:

```bash
PYTHONPATH=. python scripts/benchmark_rev0021_cpp_trace_batch.py
```

It uses the rev0020 public traces, prepares transition records once, times a single batched C++ pass, and compares that to a small one-record-per-process sample to expose subprocess overhead.  The expected lesson is that C++ kernels should be called in batches whenever possible.
