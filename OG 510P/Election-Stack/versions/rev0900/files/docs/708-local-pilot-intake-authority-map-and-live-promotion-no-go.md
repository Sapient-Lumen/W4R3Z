# Local pilot intake, authority map, and live-promotion no-go

**Track:** Shared / A

Version v833 adds a local-pilot intake layer. The goal is to turn the v832 live-pilot no-go into an actionable checklist instead of a vague warning.

## What changed

The new registry `artifacts/registries/local-pilot-intake-requirements.csv` defines the minimum local facts that must be collected before the archive is used for a live or public-support pilot. The generated reports are:

- `artifacts/reports/local-pilot-intake-matrix.json`
- `artifacts/reports/local-pilot-intake-matrix.csv`
- `artifacts/reports/local-pilot-gap-burndown.json`
- `artifacts/reports/local-pilot-gap-burndown.csv`
- `artifacts/reports/local-pilot-no-go-notice.md`

The support files are:

- `artifacts/templates/local-pilot-configuration-worksheet.md`
- `artifacts/templates/live-pilot-authority-and-contact-map.md`
- `artifacts/checklists/local-pilot-intake-checklist.md`

## Why this matters

A verifier can pass every synthetic packet and still be unsafe to use in a real jurisdiction if the local authority, contacts, channels, privacy rules, source freshness, retention rules, reviewers, witnesses, and incident-language owners are undefined. v833 makes that gap visible as a release artifact.

## Boundaries

The generated intake pack is intentionally conservative. It reports `NO_GO_LIVE_PILOT_LOCAL_INTAKE_INCOMPLETE` for this archive because the archive does not contain signed local authorization, live evidence ledgers, counsel-reviewed jurisdiction records, external-review transcripts, or an offline verification transcript for a local pilot.

The local-pilot intake pack is not live election evidence, not certification, not current voter instruction, not authorization, not a court admissibility determination, and not legal advice.

## Promotion rule

No live-pilot claim should be made until the matrix is regenerated with jurisdiction-specific evidence and every blocking row has a local evidence pointer, owner, review status, and public boundary.
