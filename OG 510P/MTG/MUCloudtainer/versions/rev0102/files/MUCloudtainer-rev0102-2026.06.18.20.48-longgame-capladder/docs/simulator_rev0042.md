# Simulator status — rev0042

The simulator itself did not receive a rules change in rev0042.

The new work is around expensive label generation from real public DecisionFrames.  The simulator still provides:

```text
public DecisionFrame boundary
hidden true state held by the referee
legal macro-action list
Python authoritative transition semantics
C++ transition shadow parity checks
```

rev0042 branch labeling used:

```text
240 branch games
0 branch truncations
42,567 C++-checked transitions
0 C++ skipped events
0 C++ mismatches
```

The simulator is still suitable for audited smoke-scale learning experiments.  Strategic claims should still require larger nontruncated payoff tables, replay samples, promotion/statistical gates, and C++ parity checks.
