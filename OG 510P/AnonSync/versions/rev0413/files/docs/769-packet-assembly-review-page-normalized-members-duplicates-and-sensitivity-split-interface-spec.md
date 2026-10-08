# Packet assembly review page — normalized members, duplicates, and sensitivity split interface spec

## Purpose

Decide whether the normalized members now form a coherent packet candidate and whether any split or hold is required before manifest/export review.

This page exists so `pack and send` becomes an assembly decision grounded in normalized lineage rather than a pile of cleaned files.

## Inputs

- raw evidence intake object
- normalization review
- normalized candidate members
- evidence plan and capture-matrix rows
- companion-case / escalation / recipient-ask context if any
- sensitivity findings

## Primary questions this page must answer

1. Which normalized members belong in the current packet candidate?
2. Which members are duplicates, rotations, alternates, or contradiction witnesses that must remain explicit?
3. Does the packet need splitting by audience, sensitivity, or ask scope before manifest/export review?
4. What packet sentence is honest about lineage from raw intake to assembled set?
5. What smallest next step should follow: manifest review, split, or additional intake work?

## Layout

### A. Assembly strip

Fields:

- packet candidate label
- normalized-member count
- lineage confidence
- split posture (`single`, `split-recommended`, `split-required`, `hold`)
- assembly verdict

### B. Member assembly table

Columns:

- normalized member
- source raw id(s)
- artifact family
- evidence-plan row coverage
- duplicate/rotation status (`primary`, `supporting-rotation`, `alternate`, `contradiction`, `none`)
- audience/sensitivity class
- packet verdict (`include`, `split-out`, `hold`, `exclude-with-note`)

### C. Lineage summary card

Show:

- raw-source count represented
- raw sources excluded with rationale
- members whose lineage is indirect or operator-supplied
- strongest honest assembly sentence

### D. Split decision card

Show:

- whether public/private or ask-specific splitting is required
- whether crash/dump material must travel separately
- whether low-sensitivity logs may travel without heavier raw dumps
- what later manifest version(s) should be created

### E. Next-step card

Show:

- `open evidence manifest`
- `split into two manifests`
- `return to normalization review`
- `request stronger provenance binding`
- `hold because packet meaning is still unstable`

## Required interactions

- `Include as packet member`
- `Mark as supporting rotation`
- `Keep as contradiction witness`
- `Split member to alternate packet`
- `Exclude with lineage note`
- `Open evidence manifest`
- `Issue intake receipt`

## Guardrails

- Never hide that one packet member came from several raw inputs.
- Never collapse duplicates and contradictions into the same semantics.
- Never allow a sensitivity split to erase lineage back to raw intake.
- Never claim packet coherence if key members still have weak source binding.
- Never let packet assembly supersede evidence-manifest review; it only prepares it.

## Output

A reviewed packet-assembly decision preserving normalized membership, duplicate/contradiction handling, split posture, and lineage confidence before manifest/export review.

