
# Artifact capture matrix page — platform route, preconditions, and return state interface spec

## Purpose

Model the practical collection matrix behind the evidence plan.
This page should answer:

- which participant or platform owes each artifact row
- how that artifact is obtained
- what preconditions or commands are required
- whether the row is collectible, blocked, partial, or returned
- what later manifest row the capture should produce

This page exists so hidden paths, service-specific storage roots, mobile special codes, and shutdown requirements stop living only in support guides.

## Inputs

- evidence plan identifier
- participant inventory and roles
- platform / runtime inventory
- artifact-family requirements
- current precondition states
- known storage paths, command routes, and capture surfaces
- returned artifacts so far
- current privacy envelope

## Primary questions this page must answer

1. Who owes each artifact row?
2. What exact capture route produces that row?
3. What prerequisites or disruptions does the row require?
4. What is the current return state of each row?
5. Which rows are blocking a complete manifest?

## Layout

### A. Matrix strip

Fields:

- evidence plan label
- incident headline
- manifest target
- blocking-row count
- current completeness posture

### B. Artifact rows table

Columns:

- row id
- participant / platform
- artifact family
- capture route (`auto-send`, `manual-file`, `hidden-folder`, `crash-harvest`, `benchmark-command`, `other`)
- source location or command surface
- prerequisites
- disruption level (`none`, `restart`, `shutdown`, `wait-for-crash`, `elevated-access`, `other`)
- expected output
- return state (`not-started`, `ready`, `collecting`, `returned`, `partial`, `blocked`, `not-collectable`)

### C. Blocking incompatibilities card

Examples:

- mobile log-size cannot be increased
- capture requires hidden-folder access
- crash artifact does not exist until a crash happens
- network benchmark requires Sync shutdown
- service-mode path differs from ordinary desktop path

### D. Row drilldown card

For the selected row show:

- why the row matters
- who is expected to perform it
- time window and dwell expectations
- exact artifact names or measurement class expected
- what later manifest line this row should satisfy

### E. Completion map card

Show:

- required rows returned
- optional rows returned
- blocking rows still open
- strongest safe sentence with current row coverage

## Required interactions

- `Mark row ready`
- `Mark row blocked`
- `Attach returned artifact`
- `Record benchmark result returned`
- `Mark row not collectable`
- `Open evidence manifest`
- `Issue evidence export receipt`

## Guardrails

- Never collapse different capture routes into one generic `collect` action.
- Never hide platform-specific paths, commands, or storage roots once a row is in scope.
- Never treat `returned` as `usable` unless the row satisfied its prerequisites.
- Never let a blocked required row disappear from completeness review.
- Never imply that one participant's row covers another participant's duty unless the plan says so explicitly.

## Output

A reviewed capture matrix that preserves artifact rows, capture route, prerequisites, disruption cost, return state, and manifest expectation.
