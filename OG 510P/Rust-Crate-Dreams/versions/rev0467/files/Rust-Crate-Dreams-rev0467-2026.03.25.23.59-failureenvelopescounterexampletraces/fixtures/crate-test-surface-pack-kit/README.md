# Crate Test Surface Pack Kit fixtures

Use this fixture family to express:
- official versus illustrative fixture/support levels,
- in-process / loopback / containerized / credentialed topology boundaries,
- deterministic seams for time, randomness, filesystem, environment, and process state,
- witness lineage for direct runs, compile-fail harnesses, and imported replay artifacts,
- snapshot normalization boundaries that stabilize outputs without pretending semantics disappeared,
- isolation class and runner-specific parallel safety,
- reset / cleanup posture and contamination windows.

The most important repo-memory rule for this lane is:

> Do not confuse **testing substrate** with **crate-authored downstream testing support**.

A good fixture pack here should make seven things explicit:

1. which fixture families are actually supported,
2. which host capabilities a representative scenario requires,
3. which scenario witnesses were observed,
4. where those witnesses came from,
5. whether the helper is actually isolated under the claimed runner,
6. how state gets reset or cleaned up again,
7. and which normalization tricks are helping determinism versus hiding real semantics.
