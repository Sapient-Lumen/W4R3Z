# rev0030 C++ core plan

The long-haul direction remains:

```text
Python = semantic reference, hidden-information boundary, replay/gates, analytics
C++    = stable hot kernels and eventual high-throughput referee core, only after parity checks
```

Completed C++ seams so far:

```text
rev0015: deck probability probe kernel
rev0016: legal-menu differential harness
rev0017: transition microkernel initial cases
rev0018: stack/choice transition expansion
rev0019: recorded-trace checker
rev0020: Jace ultimate shuffle transport
rev0021: batch trace seam
rev0026: live C++ shadow rollout
rev0030: no-choice segment fingerprint data for future segment batching
```

rev0030 did not add a new C++ kernel. That was deliberate. The new segment fingerprints identify a more coherent C++ target:

```text
batch forced no-choice segments, not individual actions
```

The next C++ implementation should consume a compact segment record and compare its post-state SIGv2/fingerprint against Python.
