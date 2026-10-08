# Retention incident response (spoliation / evidence loss)

**Track:** Shared (cross-cutting)


Use this playbook when evidence retention fails (accidental deletion, corruption, or sabotage).

## Actions
- Immediately snapshot all remaining storage and log endpoints.
- Publish an incident comms package and a `SCHEMA:schemas/DriftAlert.json` (or equivalent) describing missing artifacts.
- Activate:
  - `CHECK:artifacts/checklists/notarization-and-timestamping-checklist.md`
  - `CHECK:artifacts/checklists/evidence-publication-checklist.md`

## Follow-up
- Add new redundancy requirements and run a retention drill quarterly.
