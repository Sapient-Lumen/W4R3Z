# Scenario — cache GC mutate-exclusive activity should be modeled as a real blocking surface

This scenario exists to force **P-0490** to distinguish package-cache mutation from ordinary download or read activity.

Cargo’s current `cache_lock` docs say `MutateExclusive` acquires both underlying locks and blocks readers.
A worthy witness bundle should therefore model this as a materially different collision class from ordinary download activity.
