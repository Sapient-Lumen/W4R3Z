# Effective policy sheet page: origin, precedence, and current-force interface spec

## Purpose

This page answers one ordinary question:

> what rules are actually in force for this subject right now, which plane supplied each one, and which stronger or weaker planes were overridden?

The page exists because a resolved value without provenance is not enough.

## Core decision

Every serious subject that can inherit defaults, carry local overrides, or be config-owned must render one first-class **Effective policy sheet** page.
That page owns:

- resolved field values
- origin plane
- precedence result
- mutability from the current surface
- nearby competing defaults
- strongest safe sentence

## Fixed page order

1. subject strip
2. effective fields table
3. plane stack card
4. exception and drift card
5. future-arrivals card
6. source-of-truth rail

### 1) Subject strip

Show:

- subject label
- subject family
- scope class
- current policy posture summary
- strongest next-safe action

Scope classes must include at minimum:

- `subject-local only`
- `inherits standing default`
- `local override active`
- `future-arrivals default`
- `config-owned`
- `derived from parent cohort`

### 2) Effective fields table

For each serious field, show a row with at least:

- field name
- current value
- origin plane
- winning precedence reason
- mutable from here? yes/no
- if changed here, expected blast radius

Fields worth supporting include at minimum:

- residency / sync mode
- arrival-placement policy
- archive-bearing posture
- destructive-heal posture
- relay / tracker / LAN / known-host posture
- queue / priority posture
- any standing cohort default relevant to this subject

### 3) Plane stack card

Publish the planes in precedence order, for example:

- configuration-plane declaration
- standing cohort default
- linked-device or seat default
- subject-local override
- temporary reviewed exception

The page must say which planes were present, which plane won, and which lower plane values were superseded.

### 4) Exception and drift card

Show:

- whether this subject differs from its cohort expectation
- whether the difference is reviewed, inherited, legacy, or accidental
- who last changed it
- whether the exception is aging, expected, or ready for rejoin review

### 5) Future-arrivals card

If the current field also shapes future arrivals or future subjects, publish that separately.
The page must not let a future-arrivals default impersonate a current-subject guarantee, or vice versa.

### 6) Source-of-truth rail

Link to the latest policy-change preview, inheritance return review, drift receipt, or config ownership receipt when available.

## Rules

### Rule 1 — effective value must never appear without origin

A naked `ON`, `OFF`, `Synced`, or `Use relay` value is insufficient.
The operator must be able to see where the value came from.

### Rule 2 — precedence must be inspectable

The page must show not only the winning value, but why another plausible source lost.

### Rule 3 — config-owned subjects publish that fact loudly

If the current subject is governed by a configuration-plane declaration, the page must say so before offering UI edits that would imply local ownership.

### Rule 4 — blast radius must stay adjacent to editable fields

Any row that can be changed from this page must say whether the result applies here only, to inheriting siblings, or to future arrivals.

## Acceptance criteria

A later operator can:

- tell which value is currently in force
- tell where that value came from
- tell which competing default or override lost
- tell whether a change here is local, cohort-wide, or future-only
- tell whether the subject is UI-owned or config-owned
