# Research Opinions and Build Priorities

This document states concrete opinions after the research pass and maps them to execution choices.

References: [docs/RESEARCH_SOURCES.md](/workspace/docs/RESEARCH_SOURCES.md), [docs/RESEARCH_AGENDA.md](/workspace/docs/RESEARCH_AGENDA.md).

## Strong Opinions

1. Concord should optimize for robustness evidence, not strategy leaderboards.
2. Rust should remain the only authority for simulation semantics and artifact hashing.
3. Formal methods should be additive and staged: SMT first, probabilistic model checking second.
4. Python should orchestrate workflows and reporting, but never redefine simulation mathematics.
5. Every scientific claim must declare evidence class: empirical estimate, formal proof, or temporary assumption.
6. Anti-extortion search should never optimize raw self-payoff alone; it must record payoff asymmetry and recovery behavior.
7. Strategy-space expansions should be phased and benchmarked against simpler spaces before being treated as progress.

## What To Build First

1. Dual-solver SMT lane (`Z3` + `cvc5`) over a shared SMT-LIB emitter.
2. Cross-solver agreement and divergence artifacts as gating evidence.
3. Holdout robustness suite expansion (noise, horizon, opponent-shift, and extortion/fairness pressure).
4. Anti-vampire scorecards that track payoff asymmetry, recovery, and repair-channel abuse.
5. One compact strategy-space frontier check (memory-one vs richer/simpler adjacent spaces) as a standing benchmark.
6. Typed Rust-to-Python FFI for certification-critical functions.
7. Claim schema enforcing evidence-class tagging in reports.

Why this order:
- It strengthens correctness posture before expanding search breadth.
- It creates fast feedback for solver or semantics regressions.
- It avoids false confidence from leaderboard-only workflows.

## What To Avoid (For Now)

1. Do not launch large-scale evolutionary search before formal claim classes exist.
2. Do not make PRISM/STORM mandatory for all runs on day one; start with small stochastic worlds.
3. Do not chase many verification tools simultaneously as blocking dependencies.
4. Do not produce public “best strategy” claims without explicit failure envelope artifacts.
5. Do not let orchestration convenience bypass deterministic replay contracts.

## 12-Week Priority View

### Weeks 1-2

1. Finalize claim taxonomy and solver obligation table in specs.
2. Implement SMT-LIB emitter and baseline solver adapters.
3. Add solver replay artifacts and agreement checks.

### Weeks 3-6

1. Expand holdout and robustness matrix suites.
2. Add claim-tagged report schema and verifier.
3. Add typed FFI path for certification-critical Rust kernels.

### Weeks 7-9

1. Pilot PRISM/STORM model-checking on one stochastic world family.
2. Add simulation vs model-checking bound comparison artifacts.
3. Add divergence triage flow and ledger integration.

### Weeks 10-12

1. Harden reproducibility bundle schema and independent verifier.
2. Calibrate strict formal checks for release mode.
3. Publish first source-backed scientific report bundle.

## Decision Gates

1. Promote solver checks from advisory to required only after cross-solver stability.
2. Promote model-checking from pilot to required only after bounded world templates stabilize.
3. Promote robustness claims to external reporting only after holdout coverage thresholds are met.

## Failure Conditions

If any condition appears, freeze expansion and repair foundations:

1. Cross-solver disagreement rate spikes without clear triage.
2. Replay failures occur for previously “green” claim bundles.
3. Robustness suite regressions are hidden by aggregate leaderboard summaries.
4. Assumption backlog grows without retirements across two cycles.
