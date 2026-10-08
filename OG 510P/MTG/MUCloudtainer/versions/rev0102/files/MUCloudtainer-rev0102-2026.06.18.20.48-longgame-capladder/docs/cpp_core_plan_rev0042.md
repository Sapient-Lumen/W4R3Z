# C++ core plan as of rev0042

The long-haul direction remains C++ where it is valuable, but Python remains the semantic authority.

```text
Python = semantic reference, hidden-information boundary, replay/gates, analytics
C++    = stable hot kernels, segment/batch acceleration, future rollout core after parity proof
```

rev0042 does not add a new C++ kernel.  It routes a larger hard-frame branch workload through the existing C++ transition shadow checker:

```text
42,567 checked transitions
0 skipped transitions
0 mismatches
```

That is the correct use of C++ at this stage.  Every new label pipeline should continue to be shadowed before C++ is trusted to execute any authoritative game segment.

Near-term C++ priorities:

```text
1. Keep C++ transition shadow checks attached to branch-heavy label generation.
2. Turn no-choice segment checking into a measured execution candidate only under Python pre/post SIGv2 gates.
3. Avoid full C++ tournament authority until replay, RNG/shuffle transport, observation, and promotion gates are preserved.
```
