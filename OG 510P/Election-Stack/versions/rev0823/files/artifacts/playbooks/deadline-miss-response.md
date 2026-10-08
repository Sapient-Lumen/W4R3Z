# Deadline miss response (MMD-style evidence publication)

**Track:** Shared (cross-cutting)


Use this playbook when evidence publication deadlines are missed (or plausibly being “slow-walked”).

## Actions
- Generate and publish a signed `SCHEMA:schemas/DeadlineViolation.json`.
- Emit an `SCHEMA:schemas/InspectionSuppressionReport.json` if a public inspection challenge was ignored.
- Activate checklists:
  - `CHECK:artifacts/checklists/evidence-deadlines-checklist.md`
  - `CHECK:artifacts/checklists/evidence-publication-checklist.md`
  - `CHECK:artifacts/checklists/incident-comms-proof-checklist.md`

## What must become publicly provable
- The deadline that applied, the expected artifact, and the missed window.
- Who was responsible for publication and which witnesses/monitors observed the miss.

## Follow-up
- Open an ADR if the deadline policy is changing.
