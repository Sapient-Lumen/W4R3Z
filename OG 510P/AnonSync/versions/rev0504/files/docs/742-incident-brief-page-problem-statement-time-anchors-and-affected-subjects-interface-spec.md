# Incident brief page — problem statement, time anchors, and affected subjects interface spec

## Purpose

Give the operator one durable page that answers:

- what exact problem this incident is trying to explain
- what has actually been observed versus only inferred
- which time anchors matter
- which shares/files/subjects are in scope
- what short brief should travel with any later witness request or export

This page exists so the case does not live in freeform support text.

## Inputs

- incident identifier
- entry surface and entry symptom
- current strongest explanation and confidence
- known participants and roles
- known affected shares/files/subjects
- observed timestamps and their sources
- current witness-set strategy if any
- current claim ceiling

## Primary questions this page must answer

1. What is the shortest honest statement of the problem?
2. Which parts are directly observed facts versus current explanation?
3. Which time anchors matter for later capture or search?
4. Which subjects are definitely in scope, maybe in scope, or excluded for now?
5. What brief should be reused rather than retyped later?

## Layout

### A. Brief strip

Fields:

- incident headline
- issue class
- current strongest safe summary
- brief freshness
- current claim ceiling

### B. Observation versus explanation card

Two columns:

- **Observed now**
- **Current explanation**

The page must keep these separate.
Examples:

- observed: `Peer B stayed connected but queue did not drain.`
- explanation: `Destination may be blocked on local write or route stall.`

### C. Time anchors card

Rows may include:

- first observed time
- last reproduced time
- best-known failure window
- current timezone basis
- time source (`user-observed`, `row-history`, `system-event`, `imported-note`, `unknown`)
- time confidence (`exact`, `approximate-minute`, `approximate-hour`, `unknown`)

### D. Affected subjects card

For each current subject show:

- subject/share/file name
- scope status (`confirmed`, `candidate`, `excluded-for-now`)
- why it belongs in the brief
- whether later witness requests should inherit it automatically

### E. Reusable brief card

Show the exact structured brief that later pages should inherit:

- short problem statement
- participants in scope
- time anchors
- affected subjects
- strongest safe wording
- stronger forbidden wording

## Required interactions

- `Confirm incident brief`
- `Edit short problem statement`
- `Promote observed detail into brief`
- `Demote weak detail out of brief`
- `Add or correct time anchor`
- `Mark subject confirmed / candidate / excluded`
- `Open symptom bookmark`
- `Open coordinated capture run`
- `Issue capture brief receipt`

## Guardrails

- Never force the operator to rewrite details already known from the incident, witness plan, or history surfaces.
- Never mix observed fact and explanation in one sentence without a visible qualifier.
- Never let a loose timestamp travel without confidence and source.
- Never let a long narrative paragraph replace the structured brief fields.
- Never export a later packet without showing which brief version it inherited.

## Output

One reusable incident brief object with typed problem statement, time anchors, affected subjects, and safe-language boundary.
