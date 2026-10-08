# Surface capability page: action parity and reason-coded gaps interface spec

## Purpose

This page answers one ordinary question:

> what can this seat actually do from *this* surface right now, what is missing here, and why?

The page exists because `desktop`, `web`, `android`, `ios`, `cli`, and `narrow width` are not decorative skins.
They are capability projections with real gaps.

## Core decision

Every seat/surface pair must render one first-class **Surface capability** page.
That page owns:

- current surface identity
- action families that are available here
- action families that are unavailable here
- whether the gap is policy, platform, permissions, background state, or missing acceleration
- the strongest available fallback surface

The workbench must not force the operator to infer those truths from absent buttons.

## Primary layout

The page always renders the same regions in the same order:

1. surface strip
2. capability matrix
3. current blockers card
4. fallback / escalation card
5. recent parity receipts

### 1) Surface strip

Show:

- current surface label
- seat/runtime label
- confidence verdict: `full`, `reduced`, `degraded`, `projection-only`
- one next honest action

### 2) Capability matrix

Rows are action families, not raw buttons.
At minimum show rows for:

- open / reveal bytes
- edit in place
- external edit with save-back
- clear local bytes
- destroy globally
- restore / history access
- share / approve / revoke
- path choice / relocation
- background delivery
- diagnostic capture

Each row shows:

- `available here`
- `available with review`
- `available elsewhere only`
- `blocked`
- exact reason code

### 3) Current blockers card

Show the winning blockers, for example:

- platform sandbox
- no shell integration
- WebUI-only seat
- battery saver / auto-sleep
- forbidden network
- readonly permission
- background delivery unavailable
- missing local bytes

Each blocker names the verb family it constrains and whether the condition is mutable.

### 4) Fallback / escalation card

For every unavailable high-value action, show:

- strongest fallback action here
- stronger surface that can do the full action
- whether state or bytes must travel first
- what semantic loss the fallback introduces

### 5) Recent parity receipts

Receipts show:

- surface
- verb family
- parity verdict
- blocker or fallback reason
- who observed or approved it
- time

## Non-negotiable rules

### Rule 1 — missing UI is not a capability explanation

Absence of a control is never the primary answer.
The page must publish why the action is absent.

### Rule 2 — fallback must preserve semantic truth

If a surface can only export-copy rather than edit live, or can only queue work rather than finish it now, the page must say so explicitly.

### Rule 3 — capability must be reason-coded

`Unavailable` is insufficient.
Every gap needs a winning reason class the operator can inspect.

## Honest outputs

The page may conclude:

- `full parity here`
- `reduced but safe`
- `copy-based fallback only`
- `background-disabled surface`
- `escalate to stronger surface`

It may not collapse all surface differences into one generic `limited on mobile` or `web version` label.
