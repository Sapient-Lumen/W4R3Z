# rev0034 C++ core plan

The C++ doctrine remains unchanged:

```text
Python = semantic reference, hidden-information boundary, replay/gates, analytics
C++    = stable hot kernels, segment/batch acceleration, future rollout core after parity proof
```

rev0034 does not add a new C++ kernel.  It sends the larger action-counterfactual branch traffic and payoff evaluation traffic through the existing C++ shadow transition checker.

This is intentional.  The immediate bottleneck is label quality, not lack of C++ surface area.  The next C++ target is still no-choice/forced segment execution under Python pre/post SIGv2 gates, but only after branch-label collection becomes the measured throughput bottleneck.

## Current C++ trust ladder

```text
rev0015  deck probability probe kernel
rev0016  legal-menu differential harness
rev0017  one-action transition microkernel
rev0018  stack/choice transition expansion
rev0019  recorded-trace transition checker
rev0020  Jace ultimate shuffle transport
rev0021  batch trace seam
rev0026  live C++ shadow rollout
rev0031  no-choice segment checker
rev0032  batched segment shadow payoff
rev0034  scaled branch-label traffic shadow-checked
```
