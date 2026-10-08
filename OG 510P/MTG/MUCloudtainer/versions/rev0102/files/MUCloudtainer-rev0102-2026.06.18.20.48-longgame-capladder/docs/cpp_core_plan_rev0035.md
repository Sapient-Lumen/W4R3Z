# C++ core plan as of rev0035

The C++ direction remains unchanged and deliberately conservative.

```text
Python = semantic reference, hidden-information boundary, replay/gates, analytics
C++    = stable hot kernels, segment/batch acceleration, future rollout core after parity proof
```

rev0035 does not add a new C++ kernel.  Instead, the new budgeted branch-label
traffic and payoff evaluation are pushed through the existing C++ shadow checks.
That is the correct default: every new traffic pattern should keep exercising the
C++ parity seams before C++ is allowed to become authoritative.

Current trusted C++ seams:

```text
rev0015 deck probability probe kernel
rev0016 legal-menu differential harness
rev0017 one-action transition microkernel
rev0018 stack/choice transition expansion
rev0019 recorded trace checker
rev0020 Jace ultimate shuffle transport
rev0021 batch trace checker
rev0026 live shadow rollout
rev0031 no-choice segment checker
rev0032 batched segment shadow payoff
```

Next plausible C++ target:

```text
no-choice segment execution benchmark under Python pre/post SIGv2 gates
```

The warning from rev0032 still stands: carrying C++ state across multiple actions
finds bugs that one-action checking cannot.  Segment batching should remain a
shadow path until it is boring.
