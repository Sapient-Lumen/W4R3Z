# Simulator notes through rev0051

No simulator semantics changed in rev0051.

The revision stresses the existing simulator through a deeper terminal-clean focused panel:

```text
312 games
900 decision ceiling
0 truncations
89,750 C++ shadow transition events
0 C++ mismatches
8 replay samples passed
```

The important simulator-side behavior is continuity: focused evaluation uses the same public DecisionFrame interface, split RNG convention, replay system, terminal-clean row annotations, and C++ shadow transition checks as the broader population panels.

That means rev0051 evidence is comparable to rev0050 evidence except for the intentional difference in sampling design: rev0051 is focused on claim-ledger targets instead of full all-pairs coverage.
