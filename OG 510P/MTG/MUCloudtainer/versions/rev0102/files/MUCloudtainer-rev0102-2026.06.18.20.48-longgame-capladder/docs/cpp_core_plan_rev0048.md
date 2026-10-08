# rev0048 C++ core plan

The C++ direction remains unchanged:

```text
Python = semantic reference, hidden-information boundary, replay/gates, analytics
C++    = stable hot kernels, segment/batch acceleration, future rollout core after parity proof
```

rev0048 does not add a new C++ kernel. Instead, it attaches the existing C++ shadow checker to a longer, terminal-clean payoff panel.

Why that matters:

* Longer games exercise more action transitions.
* A higher decision ceiling can expose late-game parity bugs.
* The C++ path must remain correct under terminal-rescue evaluation, not only under short smoke games.

rev0048 C++ checks:

```text
full-panel transition shadow events: 43,088
full-panel skipped events:              0
full-panel mismatches:                  0
replay-trace events:                2,436
replay-trace skipped events:            0
replay-trace mismatches:                0
```

Next C++ target remains no-choice segment execution under Python pre/post SIGv2 gates, but only after label collection or payoff generation becomes clearly speed-limited.
