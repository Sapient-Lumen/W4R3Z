# C++ core plan after rev0041

The C++ doctrine remains:

```text
Python = semantic reference, hidden-information boundary, replay/gates, analytics
C++    = stable hot kernels, segment/batch acceleration, future rollout core after parity proof
```

rev0041 did not add a new C++ kernel. It routed another branch-heavy counterfactual selector audit through the existing C++ transition shadow checker:

```text
24,016 checked transitions
0 skipped transitions
0 mismatches
```

That is still valuable. Every new label/evaluation path exercises different state traffic. The C++ path should keep earning trust through shadow checks before it becomes authoritative.

The next C++-specific target remains no-choice segment execution under Python pre/post `SIGv2` gates, but the current bottleneck is still label quality rather than raw rollout throughput.
