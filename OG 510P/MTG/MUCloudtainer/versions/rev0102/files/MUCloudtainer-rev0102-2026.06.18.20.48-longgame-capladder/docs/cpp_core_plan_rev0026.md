# C++ core plan as of rev0026

The archive is cloudtainer-bound: future sandpeople should assume Python, local C++, NumPy/Pandas/scikit-learn/PyTorch CPU, and ordinary shell tools.  The long-haul high-performance plan is C++ where it is measurably valuable, not a blind rewrite.

## Role split

```text
Python
  semantic authority
  hidden-information boundary
  DecisionFrame construction
  replay traces
  promotion/statistical gates
  analytics and experiments

C++
  stable hot kernels
  batch transition checks
  future rollout core after differential proof
```

## Current C++ ladder

```text
rev0015  deck probability probe kernel
rev0016  legal-menu differential harness
rev0017  transition microkernel initial cases
rev0018  stack/choice transition expansion
rev0019  recorded-trace checker
rev0020  Jace ultimate explicit shuffle transport
rev0021  batch trace checker
rev0026  live shadow rollout seam
```

## Next C++ priorities

1. Keep shadow rollout attached to new evaluations.
2. Add a C++ batch rollout prototype only as a shadow lane first.
3. Benchmark Python DecisionFrame construction versus C++ transition application.
4. Only then move toward C++ authoritative rollout for selected no-RNG/no-choice segments.

## Current blocker to full C++ authority

C++ can match one-action transitions, but Python still owns:

```text
hidden-information observation redaction
agent-facing legal-frame construction
mulligan agent plumbing
promotion/replay/statistical gate metadata
RNG transcript ownership
```

A full C++ core should not bypass those boundaries.
