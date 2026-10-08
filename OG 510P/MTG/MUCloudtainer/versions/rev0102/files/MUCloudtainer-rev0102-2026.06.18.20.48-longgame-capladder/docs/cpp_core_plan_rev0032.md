# rev0032 C++ core plan

Current doctrine:

```text
Python = semantic reference, hidden-information boundary, replay/gates, analytics
C++    = stable hot kernels, segment/batch acceleration, future rollout core after parity proof
```

Completed C++ seams:

```text
rev0015: deck probability probe kernel
rev0016: legal-menu differential harness
rev0017: transition microkernel initial cases
rev0018: stack/choice transition expansion
rev0019: recorded-trace transition checker
rev0020: Jace ultimate shuffle transport
rev0021: batch trace checker
rev0026: live C++ shadow rollout
rev0031: no-choice segment checker
rev0032: batched no-choice segment finalization + actor-refresh fix
```

Near-term C++ priorities:

1. Keep using the batched segment checker on new payoff traffic.
2. Build no-choice segment **execution** benchmarks under Python pre/post fingerprints.
3. Consider a C++ rollout core only after no-choice segment execution, stack resolution, pending choices, and Jace ultimate transport remain stable across larger traffic.
4. Never let C++ become authoritative before replay, promotion, statistical, reward, and hidden-information gates agree.

The rev0032 lesson is subtle but important: carrying C++ state across a segment exposed an `actor` metadata bug that isolated one-action checks could not reveal. More batching means more speed, but also more opportunities for state-carry drift. Differential gates must remain close to the C++ boundary.
