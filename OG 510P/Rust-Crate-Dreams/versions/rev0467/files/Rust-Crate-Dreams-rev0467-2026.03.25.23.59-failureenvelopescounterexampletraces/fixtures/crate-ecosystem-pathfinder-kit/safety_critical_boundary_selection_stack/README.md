# Scenario stub — safety-critical boundary selection stack

Decision question:
> For a team using Rust near a safety-critical boundary, which crates belong inside the narrow high-assurance slice and which should stay outside it?

This scenario exists because safety-critical adopters often need decomposition rather than a universal “approved Rust stack.”
The sharper missing value is a boundary-aware choice packet, not a fake certification badge.

## Roles to fill
- narrow critical-path logic
- lower-criticality support surface
- evidence / review routing
- toolchain / target support truth
- off-ramp / replacement posture

## Expected artifacts
- `decision-brief.md`
- `scope-split.receipt.json`
- `manual-review.note.md`
- `claim-ceiling.report.json`
- `starter-set.bundle.json`

## Guardrail
Do not let “works in Rust” become “belongs inside the highest-criticality slice.”
