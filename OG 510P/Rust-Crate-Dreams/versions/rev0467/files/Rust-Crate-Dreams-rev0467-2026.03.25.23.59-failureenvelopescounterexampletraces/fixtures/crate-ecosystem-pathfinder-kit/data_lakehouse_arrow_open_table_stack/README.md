# Scenario stub — data lakehouse / Arrow / open-table stack

Decision question:
> Which crates should a team choose for a Rust data pipeline when Arrow-style interchange, open-table formats, and operational storage concerns pull in different directions?

This scenario exists because data and numerics work often looks like a pure API comparison from afar while actually hiding file-format, engine, interop, and deployment boundaries.

## Roles to fill
- interchange / columnar memory surface
- table / metadata layer
- storage / object-store or local-file posture
- compute / pipeline orchestration
- schema / compatibility / upgrade story

## Expected artifacts
- `decision-brief.md`
- `interop-surface.report.json`
- `candidate-elimination.receipt.json`
- `starter-set.bundle.json`
- `revisit-trigger.policy.json`

## Guardrail
Do not let current popularity erase long-term interop and storage-boundary costs.
