# Probe Suite — scenario tests, generators, and shrinking

Concord MUST treat tests as artifacts:
- probes are versioned,
- suites are curated,
- new probes are added when candidates fail in novel ways.

## 13.1 Two levels of testing

### Level 1 — Axiom Probes (small, crisp scenarios)
Probes isolate a principle; examples:
- single-noise defection after long trust (mercy)
- sustained exploitation (justice)
- repentance + evidence of change (restoration)
- fake apology loop (anti-vampire)
- ambiguous observation + audit (intention)
- moral luck / incapacity window (Hanlon calibration)
- need-based defection under scarcity (context sensitivity)
- preference mismatch / deception (silver rule vs platinum inference)

Each probe MAY include assertions (“repair within k”, “grudge half-life ≤ h”).

### Level 2 — World Suites (rich, stochastic worlds)
Suites mix payoffs, noise, topology, and institutions.

## 13.2 Generators (new, recommended)
A `ProbeGenerator` SHOULD exist:
- generates probes under constraints (bounded state, bounded rounds),
- samples from distributions (noise, scarcity shocks, topology),
- includes adversary templates (AlwaysD variants, extortion sweeps, fake apology).

## 13.3 Shrinking / minimization (new, required)
When a probe fails, the platform SHOULD attempt to produce a minimal counterexample:
- shrink rounds,
- shrink noise (bursty -> iid -> none),
- shrink topology (market -> fixed pair),
- shrink institutions (remove modules),
- shrink opponent strategy complexity,
while preserving the failure.

This is useful both for humans and LLMs to build intuition and debug.

## 13.4 Metamorphic relations (new, recommended)
Maintain a registry of metamorphic relations such as:
- player-swap symmetry,
- seed stability (qualitative labels stable across seeds),
- scaling stability (longer runs should not invert stable behaviors),
- monotonicity checks (more noise should not improve intention metrics).

Metamorphic counterexamples become probes.

## 13.5 Promotion gates tied to probe suites
Promotion MUST include:
- axiom probes,
- train/val suites,
- red-team robustness,
- holdout suite validation.
