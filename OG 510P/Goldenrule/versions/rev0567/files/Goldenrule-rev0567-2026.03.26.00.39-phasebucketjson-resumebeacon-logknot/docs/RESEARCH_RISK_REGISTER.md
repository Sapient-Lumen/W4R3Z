# Research Risk Register

This register tracks high-level technical and scientific risks in the current program.

Canonical machine-readable source now lives at:
- `specs/risk_register.yaml` (with generated summary in `docs/RISK_REGISTER.md`)

| risk_id | risk | impact | mitigation |
|---|---|---|---|
| RR-001 | Solver disagreement on encoded properties | false confidence in formal claims | require cross-solver diff artifacts + triage workflow |
| RR-002 | Benchmark overfitting | brittle strategy conclusions | enforce holdouts + robustness sweeps |
| RR-003 | Orchestration drift from Rust semantics | inconsistent claims | keep Rust as simulation truth boundary |
| RR-004 | Assumption backlog growth | policy debt and silent drift | weekly ledger review and sunset triggers |
| RR-005 | Artifact incompleteness | irreproducible results | schema checks + release manifest checks |
| RR-006 | Test-time regressions in fast loops | reduced developer feedback quality | timing baseline guardrails |
| RR-007 | Strategy-space expansion masquerading as scientific progress | misleading benchmark conclusions | phased space expansion + heterogeneous-space checks + anti-vampire scorecards |

## Review Cadence

- Update this register each time a tranche wave changes solver, benchmark, or release policy behavior.
