# Formal Methods Posture

Concord treats formal methods as a control layer that audits scientific claims.

## Scope

- Rust simulation is execution truth for trajectories and artifacts.
- Python certification is analytic truth for memory-one stationary outcomes.
- Solver tooling (z3/cvc5) is optional in development and may be strict in release posture.

## Minimum Guarantees

- Deterministic certification invariants are checked by `make test-formal-smoke`.
- Tool availability is recorded by `make test-formal-tools`.
- Formal artifacts are written under `artifacts/formal/`.

## Invariants Checked

- Stationary distribution is length 4, non-negative, and sums to 1.
- Average payoffs remain in Prisoner's Dilemma bounds `[0, 5]`.
- Identical strategy pairings satisfy payoff symmetry.
- Canonical deterministic pairs reproduce known fixed outcomes.

## Escalation

If invariants fail:

1. Freeze baseline bumps.
2. Record evidence in `artifacts/formal/`.
3. Open or update `specs/spec_ledger.yaml` before changing semantics.
