# C++ core plan after rev0040

The C++ doctrine remains unchanged:

```text
Python = semantic reference, hidden-information boundary, replay/gates, analytics
C++    = stable hot kernels, segment/batch acceleration, future rollout core after parity proof
```

rev0040 did not add a new C++ kernel. It routed another branch-heavy selector audit through the existing C++ transition shadow path:

```text
28,254 checked transitions
0 skipped transitions
0 mismatches
```

That is valuable because every new label/evaluation path creates fresh engine traffic. The safest long-haul path is still:

```text
1. keep Python authoritative
2. attach C++ shadow checks to new traffic
3. batch no-choice segments where safe
4. port only stable hot kernels
5. never let C++ bypass replay/fingerprint gates
```

The next C++-specific target remains no-choice segment execution under Python pre/post SIGv2 gates, but only after the branch-label pipeline becomes the clear speed bottleneck.
