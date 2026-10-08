# crate-authority-surface-pack-kit fixtures

This fixture pack exists to keep **P-0519 Crate Authority Surface Pack Kit** honest about six distinct questions:

1. **authority budget** — which ambient powers are required, optional, forbidden, or test-only in a named profile;
2. **injection boundary** — whether a dependency is ambient-only, injectable at construction, injectable per operation, or host-supplied;
3. **authority origin** — where the power actually comes from;
4. **fallback order** — which route is preferred before authority widens;
5. **refusal posture** — what happens when the host denies access;
6. **profile witness** — whether an advertised offline / deterministic / sandbox-ready profile actually survives a restricted recipe.

The fixtures here should bias toward cases where raw import scans are not enough:

- capability-oriented tempdir paths that should beat ambient temp discovery,
- project-dir or `$HOME` fallbacks that quietly widen an “offline” profile,
- entropy-source choices that are owned by the root crate rather than an upstream library,
- denied authority that silently degrades into a broader ambient path instead of failing honestly.

A good authority-surface crate should stay conservative in all of those cases.
