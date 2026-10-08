# Key compromise response playbook (operator / witness / signing keys)

**Track:** Shared (cross-cutting)


This playbook is activated when any key used for signing election evidence may be compromised.

## Immediate actions (first hour)
- Freeze signing and publish a signed `hfv.public.notice` PublicNotice (notice_type: incident_declaration) with current known scope.
- Trigger `CHECK:artifacts/checklists/key-compromise-response-checklist.md` and `CHECK:artifacts/checklists/incident-comms-proof-checklist.md`.
- Rotate keys using the documented ceremony:
  - `CHECK:artifacts/checklists/key-ceremony-checklist.md`
  - `CHECK:artifacts/checklists/key-destruction-ceremony-checklist.md`

## Evidence obligations
- Publish a `SCHEMA:schemas/KeyCompromiseEvent.json` describing:
  - time window, impacted roles, and affected artifacts
- Publish a checkpointed transparency-log entry stating:
  - what is considered invalid, and from which time onward

## Recovery
- Re-issue witness sets / endorsements per `DOC:docs/144-staleness-and-tombstones-for-parameter-migrations.md`
- Run an audit drill: `CHECK:artifacts/checklists/mirror-consistency-audit-checklist.md`
