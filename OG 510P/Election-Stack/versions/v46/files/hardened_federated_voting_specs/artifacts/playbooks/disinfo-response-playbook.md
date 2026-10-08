# Disinformation response playbook (evidence artifact targeting)

Use this playbook when a disinformation campaign targets evidence artifacts, results packages, or mirrors.

## Actions
- Activate:
  - `CHECK:artifacts/checklists/results-disclosure-policy-checklist.md`
  - `CHECK:artifacts/checklists/incident-comms-proof-checklist.md`
- Publish a signed `SCHEMA:schemas/IncidentCommsPackage.json` that includes:
  - canonical artifact hashes, mirror list, and verification steps

## Evidence obligations
- Ensure a third-party can verify without privileged access (observer kit).
