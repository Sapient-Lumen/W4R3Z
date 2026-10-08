# CI Policy

Concord CI maintains a deterministic smoke path and language-specific confidence jobs.

## Required CI Guarantees

- A smoke job runs `make test-quick`.
- Timing artifacts are uploaded from `artifacts/timing/`.
- Rust and Python dedicated jobs run compile/test checks.

## Local Mirrors

Equivalent local checks:

- `make test-quick`
- `make gate`
