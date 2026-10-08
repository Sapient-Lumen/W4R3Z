# Scenario stub — robotics control-loop vs operations stack

Decision question:
> For a robotics or digital-twin system, should the same crate defaults serve the control loop, simulation, telemetry, and operations planes?

This scenario exists because robotics-flavored systems often combine timing-sensitive logic with much softer diagnostics, storage, networking, and fleet workflows.
Flattening those into one stack usually hides important boundaries.

## Roles to fill
- control-loop / timing-sensitive core
- simulation / digital-twin surface
- telemetry / logging / replay
- ops / upgrade / incident tooling
- mixed-language / hardware boundary if present

## Expected artifacts
- `scope-split.receipt.json`
- `decision-brief.md`
- `candidate-elimination.receipt.json`
- `starter-set.bundle.json`
- `manual-review.note.md`

## Guardrail
Do not let an operations-friendly stack silently become the default for the control loop.
