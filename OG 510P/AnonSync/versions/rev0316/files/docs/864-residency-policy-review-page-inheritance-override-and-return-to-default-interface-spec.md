# Residency policy review page: inheritance, override, and return-to-default interface spec

## Purpose

This page exists because residency behavior often has several policy planes at once:

- line-wide defaults
- seat defaults
- subject overrides
- temporary expedited changes
- receipt replays

The dangerous ambiguity is not only `what is selected now`.
It is also:

> if I set a subject to neutral/default again, did I truly restore inheritance, or did I leave behind a sticky local override that only looks neutral?

## Core decision

AnonSync should make **residency policy review** first-class.
Any change that can alter local-presence behavior must preview:

- what policy plane is being edited
- what future inheritance survives
- whether neutral restores inheritance or merely copies a neutral value into a frozen local slot
- what receipts later prove the result

## Fixed review order

1. **Policy delta**
2. **Current inheritance stack**
3. **After-change inheritance stack**
4. **Neutral/default meaning**
5. **Subjects touched now and later**
6. **Receipts and rollback**

### 1) Policy delta

Show:

- current policy source
- proposed policy source
- current guarantee class
- projected guarantee class after change
- whether this is a live subject-only change or a standing default mutation

### 2) Current inheritance stack

Show the stack in descending precedence:

- line default
- seat default
- subject override
- temporary review / receipt replay

Each row must show whether it is active, shadowed, or absent.

### 3) After-change inheritance stack

This section must say plainly:

- which rows stay authoritative
- which rows become shadowed
- whether the subject will keep tracking higher-level changes afterward
- which later policy changes will still reach this subject

### 4) Neutral/default meaning

This section is mandatory.
It must resolve to one explicit result:

- `return to inheritance`
- `store explicit neutral value`
- `clear temporary override only`
- `ambiguous; blocked pending clarification`

AnonSync hard decision:

- the default behavior must be `return to inheritance`
- storing an explicit neutral value is allowed only as an expert-only deliberate choice with a stronger warning

### 5) Subjects touched now and later

Show two lists:

- **current scope touched now**
- **future subjects affected later**

Examples:

- `this subtree only`
- `future descendants under this subtree`
- `all new subjects on this seat`
- `no future subjects; current realization only`

### 6) Receipts and rollback

The page must preview the receipt fields:

- prior policy source
- resulting policy source
- inheritance restored? (`yes` / `no`)
- future subjects affected? (`yes` / `no`)
- nearest rollback path

## Rules

### Rule 1 — neutral is semantic, not cosmetic

The product may not let `None`, `Default`, or `Auto` mean one thing visually and another thing in inheritance behavior.

### Rule 2 — the page must preview future drift

If a subject will stop following later line/seat changes, the page must say so before commit.

### Rule 3 — expert sticky neutral must stay explicit

A frozen local neutral value is sometimes useful, but it must never be the quiet default.

### Rule 4 — current-local and future-default edits may not blur together

The review must separate `change what is local now` from `change what future arrivals will do`.

## Suggested action rows

- `Restore inheritance`
- `Freeze subject override`
- `Edit seat default`
- `Apply temporary expedite only`
- `Cancel and inspect current residency intent`

Each row should show:

- scope
- future impact
- receipt emitted
- nearest rollback path

## Acceptance criteria

A later operator can:

- tell exactly which policy plane changed
- know whether neutral/default truly restored inheritance
- know whether future descendants or future subjects are affected
- read a receipt later and recover the same answer without replaying UI history
