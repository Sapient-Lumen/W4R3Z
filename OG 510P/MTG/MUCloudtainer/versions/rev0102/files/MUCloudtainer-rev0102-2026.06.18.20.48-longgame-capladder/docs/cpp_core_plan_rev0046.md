# rev0046 C++ core plan

No new C++ kernel was added in rev0046.  That was deliberate.

The new yield-screen branch-heavy traffic was routed through the existing C++ transition shadow checker:

```text
20,453 checked transitions
0 skipped events
0 mismatches
```

The standing doctrine remains:

```text
Python = semantic reference, hidden-information boundary, replay/gates, analytics
C++    = stable hot kernels, segment/batch acceleration, future rollout core after parity proof
```

The next C++ work should only happen when branch collection or payoff rollout speed becomes the measured bottleneck.  Until then, every new label collector should keep C++ as a shadow parity checker.
