# Scenario stub — desktop GUI teaching vs shipping stack

Decision question:
> For a desktop GUI app, should the recommended teaching stack and the recommended shipping stack be the same?

This scenario exists because GUI work has a special kind of compile / iteration pain and often pulls in platform packaging, diagnostics, and state-management tradeoffs that are easy to flatten into one vague recommendation.

## Roles to fill
- UI toolkit
- app lifecycle / state
- logging / diagnostics
- packaging / updater route
- debug / iteration support

## Expected artifacts
- `scope-split.receipt.json`
- `decision-brief.md`
- `candidate-elimination.receipt.json`
- `starter-set.bundle.json`
- optional `manual-review.note.md`

## Guardrail
Do not force a single answer if teaching ergonomics and shipping maturity clearly diverge.
