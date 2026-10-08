# Science Plan

This plan treats Concord as a reproducible computational science system, not a narrative artifact.

Source-backed foundation:
- Research bibliography: [docs/RESEARCH_SOURCES.md](RESEARCH_SOURCES.md)
- Expanded execution agenda: [docs/RESEARCH_AGENDA.md](RESEARCH_AGENDA.md)

## Objective

Produce defensible strategy claims under explicit world definitions, deterministic seeds, and auditable evidence artifacts.

## Phase A: Deterministic Core (active)

1. Keep deterministic harness and integration gate healthy (`make test-quick`, `make test-full`, `make gate`).
2. Keep Rust as simulation/artifact truth and Python as orchestration/reporting truth.
3. Keep governance validators (goldens, ADR, spec ledger, docs/index integrity) blocking in `gate`.

## Phase B: Formal Claim Strengthening (next)

1. Add dual-solver SMT lane (Z3 + cvc5) under shared SMT-LIB contracts.
2. Add cross-solver agreement artifacts and discrepancy triage.
3. Add probabilistic model-checking pilot lane (PRISM/STORM) for small stochastic worlds.
4. Tie formal obligations to claim classes in specs.

## Phase C: Robustness and Benchmarking

1. Expand holdout/adversary suites with noise/horizon/population sweeps.
2. Integrate benchmark interoperability lanes with Axelrod/OpenSpiel references where feasible.
3. Promote robustness metrics over single-opponent scoreboard metrics.
4. Require uncertainty decomposition artifacts in reports.

## Phase D: Release-Grade Scientific Operations

1. Run strict release posture (`make gate-strict`) with security tooling and release manifests.
2. Enforce reproducibility bundle completeness and replay verification.
3. Promote soak/cadence checks to strict blocking once calibrated.
4. Keep dependency/security allowlist expiration auditable.

## Terminology Policy

- Preferred terms: `candidate`, `adversary`, `baseline`.
- Legacy terms are supported in compatibility paths until migration is complete.

## Exit Criteria

1. `make gate` is green in clean environments.
2. Claims are mapped to artifacts, tests, and explicit assumptions.
3. Deterministic reruns from seed artifacts are reliable.
4. At least one robustness suite and one formal-certification suite are active and versioned.
