
# Evidence export receipt page — plan, manifest, transport, and stale boundary interface spec

## Purpose

Leave one durable record of what package was exported, why it existed, and what the export actually proved.
This page should answer:

- which evidence plan version was used
- which manifest version actually traveled
- which transport lane was used
- what delivery state occurred
- what claim ceiling and stale boundary now apply

This page exists so `logs sent` becomes a typed receipt rather than remembered support ritual.

## Inputs

- incident identifier
- evidence plan version
- artifact capture matrix summary
- evidence manifest version
- chosen export lane
- delivery status and timestamps
- current claim ceiling
- later regeneration triggers

## Layout

### A. Export strip

Fields:

- incident headline
- export receipt id
- evidence plan version
- manifest version
- export lane (`local-save`, `shared-link`, `ticket-upload`, `peer-handoff`, `other`)
- receipt freshness

### B. Package meaning card

Show:

- target diagnostic question
- required rows satisfied at export time
- optional rows included
- strongest honest statement about what the package contains
- stronger forbidden statement

### C. Transport and delivery card

Show:

- route used
- delivery state (`queued`, `sending`, `delivered`, `delivery-uncertain`, `failed`, `saved-local-only`)
- transport caveats
- whether delivery success is separate from diagnostic sufficiency
- any follow-up expected from the recipient side

### D. Manifest summary table

Columns:

- artifact family
- member count
- participant / platform coverage
- sensitivity posture
- completeness posture
- notes

### E. Reopen and stale boundary card

Show conditions such as:

- newer manifest supersedes this receipt
- missing required row later arrives
- incident brief or witness set changed
- topology / platform inventory changed
- sensitive members were split out after this export
- the target question changed enough that this export is no longer the right package

## Required interactions

- `Copy export receipt summary`
- `Open evidence plan`
- `Open artifact capture matrix`
- `Open evidence manifest`
- `Reopen evidence planning`
- `Create successor manifest`

## Guardrails

- Never equate `delivered` with `diagnostically sufficient`.
- Never omit the plan or manifest version used.
- Never hide which transport lane was used.
- Never merge `failed delivery` and `saved locally` into one result.
- Never let a successor package silently overwrite this receipt in chronology.

## Output

A durable export receipt that preserves package meaning, manifest version, transport lane, delivery state, claim ceiling, and stale/reopen boundary.
