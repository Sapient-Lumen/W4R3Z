# Claim Taxonomy

Concord claim classes are defined in [specs/claim_classes.yaml](/workspace/specs/claim_classes.yaml).

## Purpose

This taxonomy separates empirical estimates from formal guarantees and operational reproducibility assertions.

## Evidence Classes

1. `empirical`: measured behavior under declared worlds/suites.
2. `formal`: solver-checked invariants and agreement claims.
3. `hybrid`: simulation + formal/model-checking consistency claims.
4. `operational`: reproducibility and release-manifest integrity claims.
5. `assumption`: temporary policy/behavior claims pending spec closure.

## Required Metadata Per Claim

1. claim class id (`CC-*`)
2. artifact pointers
3. required checks run
4. strict-gate requirement flag
5. explicit summary and scope

## Policy

- No report claim without a declared claim class.
- Claim class definitions must stay machine-validated.
- Strict-gate-required classes are release-blocking.
