# C++ core plan as of rev0039

The C++ doctrine remains unchanged:

```text
Python = semantic reference, hidden-information boundary, replay/gates, analytics
C++    = stable hot kernels, segment/batch acceleration, future rollout core after parity proof
```

rev0039 does not add a new C++ kernel.  It routes the matched label audit through the existing C++ transition checker:

```text
24,373 checked transitions
0 skipped transitions
0 mismatches
```

This is the correct use of C++ at this stage: every new data-collection path should stress the same transition shadow path before we trust it for learning labels.

Next C++ work remains:

```text
1. no-choice segment execution benchmark under Python pre/post SIGv2 gates
2. branch-heavy label collection with segment batching where possible
3. only then a partial rollout accelerator
```
