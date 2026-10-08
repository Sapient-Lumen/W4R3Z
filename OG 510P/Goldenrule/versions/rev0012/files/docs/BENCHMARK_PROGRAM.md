# Benchmark Program

This program defines how Concord evaluates repeated-game strategy behavior without overfitting to a single suite.

## Benchmark Families

1. Baseline deterministic worlds.
2. Noise/horizon robustness sweeps.
3. Holdout adversary suites.
4. Population-dynamics stress suites.
5. Negative-control suites (expected non-dominance).

## Required Benchmark Outputs

1. run metadata and seed reports
2. suite summary artifacts
3. failure-envelope summary
4. claim class mapping (`CC-*`)

## Benchmark Governance

1. New benchmark families require spec updates and schema validation.
2. Baseline changes require recorded rationale in docs/ADR/ledger.
3. Public-facing benchmark claims must include holdout context.
