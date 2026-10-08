# Experiment Protocol

## Objective

Run deterministic, reproducible repeated-game experiments with explicit definitions and traceable outputs.

## Standard Procedure

1. Validate environment: `make doctor`.
2. Validate fast loop: `make test-quick`.
3. Run target experiment (`python3 -m grlab ...`).
4. Record outputs under `runs/<run_id>/` and `artifacts/`.
5. Validate integrity with `python3 -m grlab verify` or equivalent checks.
6. Re-run using fixed seeds to verify replayability.

## Mandatory Metadata

- seed
- definition hashes
- world id/hash
- strategy ids/hashes
- environment metadata (OS/arch/tool versions)

## Failure Handling

- Never patch over nondeterminism without a seed replay attempt.
- Use shrink/diff tools to isolate regressions before changing logic.
