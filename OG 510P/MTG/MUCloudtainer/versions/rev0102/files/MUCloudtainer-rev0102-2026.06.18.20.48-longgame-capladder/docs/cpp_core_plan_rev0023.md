# rev0023 — C++ core plan

The long-haul direction is C++ where suitable, but Python remains the semantic reference until C++ earns each seam by differential testing.

## Current split

```text
Python
  reference semantics
  hidden-information observations
  replay/promotion/statistical/reward gates
  analytics and data generation

C++
  stable hot kernels
  legal-menu mirrors
  transition microkernels
  batch trace checking
  later: rollout acceleration
```

## Completed C++ seams

```text
rev0015: deck probability probe kernel
rev0016: legal-menu differential harness
rev0017: transition microkernel seed
rev0018: stack and choice transition expansion
rev0019: recorded-trace transition checker
rev0020: Jace ultimate shuffle transport
rev0021: batch trace preparation/finalization seam
rev0022: new policy traffic checked with batched C++ trace gates
rev0023: MLP and mulligan-gate traffic checked against the existing C++ trace seam
```

## Rule

Do not port the whole simulator just because C++ is available. Port stable, measured, replayable seams. Every C++ step should have:

```text
Python authoritative pre/post state
explicit randomness transport when needed
SIGv2 or successor state signature
zero-mismatch differential checks
coverage debt listed, not hidden
```

## Next C++ target

The next worthwhile C++ build is not a new policy. It is a batch rollout sketch over already-prepared trace records, plus a measurement of where the Python shell is still doing unavoidable semantic work. If that looks clean, only then should we attempt a C++ rollout core for a restricted no-debug/no-log tournament path.
