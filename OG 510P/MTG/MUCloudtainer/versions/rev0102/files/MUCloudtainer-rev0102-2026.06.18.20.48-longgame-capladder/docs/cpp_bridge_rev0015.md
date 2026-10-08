# rev0015 C++ bridge and cloudtainer-bound engine plan

rev0015 accepts the long-haul direction: the Python implementation is the research shell, but stable hot paths should migrate to C++ when measurement says the move is worth it.

The first C++ artifact is deliberately small:

```text
cpp/muc5_probe_kernel.cpp
src/muc5/cpp_accel.py
scripts/benchmark_cpp_probe_rev0015.py
```

It accelerates exact hypergeometric deck probes used by constructor screening, MAP-Elites archives, and evolutionary candidate generation. It is **not** the game referee yet.

## Why not rewrite the whole engine now?

The current Python referee still changes often. A premature C++ port would freeze unstable abstractions and make rule bugs harder to fix. The sensible path is:

```text
1. Keep Python referee authoritative while semantics are moving.
2. Add tiny C++ kernels for stable, measurable hotspots.
3. Preserve the public DecisionFrame/action-index contract.
4. Differential-test C++ outputs against Python reference outputs.
5. Promote C++ only when tests, replay traces, and profiles agree.
```

## Current C++ result

This cloudtainer has `/usr/bin/g++`, and the rev0015 probe kernel compiled successfully during the benchmark.

The benchmark compares 50,000 C++ probe rows against a 2,000-row Python sample, with exact-agreement tolerance against the Python reference. In this run, the C++ probe table path was about 32x faster than the sampled Python loop for the exact same probe formulas.

The generated benchmark artifacts are:

```text
data/rev0015_cpp_probe_benchmark.json
data/rev0015_cpp_probe_top10.csv
```

## Long-haul C++ core plan

The likely C++ migration order is:

```text
A. exact deck probes and static constructor filters          ✅ rev0015 seed
B. legal-action enumeration for common decision frames       later
C. compact state transition for public rollout loops         later
D. replay-fingerprint-compatible C++ referee                 later
E. Python wrapper for agents/search/analysis                 always
```

The important boundary is that C++ must not receive special strategic authority. It is a faster referee/probe implementation behind the same public/hidden-information contract.

## Portability note for future sandpeople

This archive is cloudtainer-bound. Do not assume system-wide package installation, internet access from Python, GPU availability, or long-lived background services. Generated C++ artifacts should compile from source inside the archive with tools already present in the cloudtainer. If compilation fails, Python reference code should remain usable.
