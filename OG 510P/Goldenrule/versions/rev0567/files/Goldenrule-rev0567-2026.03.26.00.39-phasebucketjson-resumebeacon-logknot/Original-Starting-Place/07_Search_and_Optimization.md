# Search & Optimization (multi-objective, adversarial, analytic)

Concord searches over strategy space under a multi-objective scorecard while adversarially growing the test suite.

## 7.1 Search modes (must)
- parameter sweeps
- evolutionary search (mutation + selection on Pareto frontier)
- adversarial coevolution (opponents/worlds generated to break candidates)
- Bayesian optimization (optional)

## 7.2 Micro-lab search (intuition juicing)
Support a cheap loop:
- mutate a candidate,
- run on a handful of probes,
- inspect trace diffs,
- repeat.

## 7.3 Property-based probe generation (recommended)
Support randomized generation + shrinking of failing probes.

## 7.4 Metamorphic testing (recommended)
Support oracle-free relations: symmetry, scaling stability, monotonicity, seed stability.

## 7.5 Proof-like artifacts (optional but high leverage)
Provide analytic certificates where possible (e.g., Markov-chain payoffs for memory-one families) and cross-check with simulation.

## 7.6 Definition hygiene (required for meaningful comparison)
Because “Golden Rule” is plural, comparisons are only meaningful when we can say:
- which scorecard we used,
- which probes/suites we used,
- which holdouts we used.

Therefore the platform MUST make definition clarity effortless:
- evaluation snapshots are versioned (scorecard/probes/holdouts hashes),
- probe registries are append-only with explicit version bumps,
- definition diffs exist for comparisons across changes.

This is about enabling autonomy (you can change things!) while keeping results interpretable.

## 7.7 Low-hanging fruit defaults (recommended)
- a small “frozen” core probe suite that changes rarely (anchor for continuity),
- at least one holdout suite,
- metamorphic checks in CI,
- a “canary adversary” set that must never regress,
- random spot-check probes not used in search (helps detect suite capture).

## 7.8 Promotion policy (must)
Promotion requires:
- passing probes and train/val suites,
- red-team passes,
- holdout validation,
- explanation artifacts (minimal repro + narrative).
