# ADR-0001-test-gate-philosophy

Status: accepted
Date: 2026-03-03

## Context

Concord needs deterministic, low-latency feedback loops while preserving stronger integration and release checks.

## Decision

Adopt a two-level gate model:
- `make test-quick` and `make test-full` are deterministic harness entry points with seed and timing artifacts.
- `make gate` is required integration posture and includes governance plus non-strict security checks.
- `make gate-strict` layers strict security and release-oriented outputs (SBOM/release artifacts).

## Consequences

The local loop remains fast and reproducible, while release posture can tighten over time without blocking exploratory work.

## Supersedes

None.
