# Chrony independent observation evaluator — rev0124

## Purpose

The rev0124 evaluator is a second implementation over the adapter boundary:

```text
chronyc text/capture -> chrony_observation JSON -> independent P1 evaluation
```

It is deliberately not a second chronyc parser. The boundary under test is the typed observation object produced by the adapter.

## What it recomputes

`tools/chrony_observation_eval.py` recomputes:

- exact collection age from `collected_at` and `evaluated_at`;
- conservative base bound: `abs(system_time_offset) + root_dispersion + 0.5 * max(root_delay, 0)`;
- skew-based holdover growth;
- nanosecond-rounded interval endpoints centered on `evaluated_at`;
- source posture from selected/combined source counts and reference ID;
- P1 satisfied, coarse-logging fallback, display-only fallback, and fail-closed decisions;
- policy acceptance, actionability, and machine-readable explanation fields.

## What the self-test compares

The self-test runs the primary adapter for every successful case in `tests/chrony-adapter-golden.yaml`, extracts the emitted `chrony_observation`, and independently evaluates it. It requires exact match for `local_assessed_state` and key explanation fields.

## Why this matters

Before rev0124, generated examples and golden cases were all downstream of the same evaluator. A logic error could become self-consistent. The independent evaluator makes a primary-evaluator regression visible at the typed-observation boundary without adding a new TimeState field.
