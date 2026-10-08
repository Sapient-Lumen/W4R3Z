
# Evidence manifest page — membership, sensitivity, and export readiness interface spec

## Purpose

Give the operator one inspectable page for what the package actually contains.
This page should answer:

- which artifacts are members of the package
- which plan rows they satisfy
- what sensitivity findings remain
- what completeness ceiling the manifest carries
- whether the package is ready for export, split, or further review

This page exists so `we sent something` stops standing in for `we know what is in the package`.

## Inputs

- evidence plan identifier and version
- artifact capture matrix rows and return states
- staged artifacts and measurements
- redaction / privacy findings
- current claim ceiling
- intended export lane

## Primary questions this page must answer

1. What exact artifacts or measurements are in this manifest?
2. Which required plan rows are satisfied, missing, or partial?
3. What path, identity, or sensitivity findings still matter?
4. What strongest claim can this manifest honestly support?
5. Is this manifest ready to export, or does it still need narrowing, splitting, or widening?

## Layout

### A. Manifest strip

Fields:

- manifest label
- evidence plan version
- incident headline
- member count
- manifest state (`draft`, `reviewed`, `ready`, `split-required`, `blocked`, `exported`)

### B. Members table

Columns:

- member
- artifact family
- source row
- source participant / platform
- time window covered
- size or measurement summary
- sensitivity flags
- member state (`included`, `excluded`, `pending-review`)

### C. Sensitivity findings card

Possible findings:

- full paths exposed
- peer/device identifiers exposed
- network addresses exposed
- crash memory or raw dump material present
- hidden-platform or service-path disclosure present
- benchmark results present without surrounding logs
- mixed-sensitivity package that should be split

### D. Completeness and claim card

Show:

- required rows satisfied versus missing
- strongest honest statement this manifest supports
- stronger forbidden statement
- contradiction or ambiguity still unresolved
- whether export should be local-only, shared, or split first

### E. Export readiness card

Show:

- target export lane
- plan version and manifest version that will travel
- missing review steps if any
- stale triggers that would force manifest regeneration

## Required interactions

- `Include member`
- `Exclude member`
- `Split manifest`
- `Open source capture row`
- `Approve export readiness`
- `Block export`
- `Issue evidence export receipt`

## Guardrails

- Never export a member that is not visible in the manifest.
- Never let `required row missing` coexist with `manifest complete` language.
- Never hide mixed-sensitivity packages behind one green success state.
- Never imply that manifest membership proves the leading explanation.
- Never allow a later receipt to omit which manifest version actually traveled.

## Output

A reviewed evidence manifest that makes package membership, sensitivity, completeness, and export readiness explicit before any outbound handoff.
