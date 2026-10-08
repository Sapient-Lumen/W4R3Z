# rev0050 C++ core plan

No new C++ kernel was added in rev0050.  That was deliberate.

The current doctrine remains:

```text
Python = semantic reference, hidden-information boundary, replay/gates, analytics
C++    = stable hot kernels, segment/batch acceleration, future rollout core after parity proof
```

rev0050 stress-tested the existing C++ transition shadow path on a larger terminal-clean population panel:

```text
256 public games
76,375 C++-checked transition events
0 skipped transitions
0 mismatches
```

Next C++ work should still be driven by measured bottlenecks, not by aesthetic desire to port everything.  The near-term C++ target remains no-choice segment execution under Python pre/post SIGv2 gates if branch-heavy data collection becomes speed-limited.
