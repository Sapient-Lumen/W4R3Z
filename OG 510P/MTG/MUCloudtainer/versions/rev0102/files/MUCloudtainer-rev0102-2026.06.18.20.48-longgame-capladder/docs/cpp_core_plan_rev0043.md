# C++ core plan rev0043

The C++ doctrine is unchanged:

```text
Python = semantic reference, hidden-information boundary, replay/gates, analytics
C++    = stable hot kernels, segment/batch acceleration, future rollout core after parity proof
```

rev0043 does not add a new C++ kernel. It deliberately routes the new online branch-collection traffic through the existing batched C++ transition checker.

## Why no new C++ code this turn?

The bottleneck this turn was not a missing C++ primitive. It was label quality and allocation: deciding which expensive branches to run. The right C++ role was therefore to shadow the new traffic and prove the existing transition kernel still agrees with Python.

Archived rev0043 C++ shadow result:

```text
checked transitions: 12,431
skipped transitions:      0
mismatches:               0
```

## Next C++ candidate

The next performance candidate remains no-choice segment execution under Python pre/post `SIGv2` gates. It should be pursued when branch collection runtime, not label quality, becomes the limiting factor.
