# rev0022 C++ core plan

The C++ direction remains:

```text
Python = semantic authority, hidden-information boundary, replay/gates, analytics
C++    = stable hot kernels and batch execution, promoted only after differential tests
```

Completed C++ seams so far:

```text
rev0015: deck probability probe kernel
rev0016: legal-menu differential harness
rev0017: transition microkernel initial cases
rev0018: stack/choice transition expansion
rev0019: recorded-trace transition checker
rev0020: Jace ultimate shuffle transport
rev0021: batched recorded-trace checker
rev0022: use batch C++ trace gate in new race/evaluation outputs
```

No new C++ kernel was added in rev0022 because the best engineering move was to make sure new learning/evaluation tables are C++-checked through the existing batch seam.

## Next C++ target

A future C++ rollout core should start from recorded traces and prepared transition batches, not from a blind port of the entire Python engine.

Minimum next contract:

```text
input: compact state/action records in batch
output: post-state SIGv2 batch
required: exact match against Python reference traces
```

Only after that should we consider a C++ loop that owns multiple whole games.
