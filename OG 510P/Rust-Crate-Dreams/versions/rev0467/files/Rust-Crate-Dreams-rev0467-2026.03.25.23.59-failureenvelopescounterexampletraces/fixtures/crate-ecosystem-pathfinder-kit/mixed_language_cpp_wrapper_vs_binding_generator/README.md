# Scenario stub — mixed-language C++ wrapper vs binding generator

Decision question:
> Should a team prefer a wrapper-style interop crate, a binding generator, or a thinner ABI layer for a C++ integration surface?

This scenario exists because interop stacks often look similar at the API layer while hiding very different toolchain, build, lock-in, and migration costs.

## Roles to fill
- foreign interface surface
- build integration
- native prerequisite story
- test / CI route
- migration / off-ramp posture

## Expected artifacts
- `lockin-cost.report.json`
- `external-prerequisite.report.json`
- `candidate-elimination.receipt.json`
- `decision-brief.md`
- `starter-set.bundle.json`

## Guardrail
Do not let code-generation convenience erase ABI, toolchain, and migration boundaries.
