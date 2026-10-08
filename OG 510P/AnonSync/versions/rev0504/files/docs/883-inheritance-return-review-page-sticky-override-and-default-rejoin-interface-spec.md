# Inheritance return review page: sticky override refusal and default rejoin interface spec

## Purpose

This page answers one ordinary question:

> when I say `return to default`, am I really rejoining inheritance, or am I leaving behind a hidden local exception that merely looks neutral?

The page exists because `None`, `Auto`, or `Default` is not automatically the same thing as true inheritance.

## Core decision

Whenever a subject leaves an explicit override and claims to return to a parent/default rule, the product must render a first-class **Inheritance return review** page.

## Fixed page order

1. return strip
2. parent-rule card
3. sticky-exception test card
4. future-reaction card
5. rejoin receipt preview
6. commit boundary

### 1) Return strip

Show:

- current explicit override
- claimed destination default
- source cohort or parent
- strongest next-safe action

### 2) Parent-rule card

Publish the exact parent/default rule that will be inherited after rejoin, including:

- current inherited value
- owning plane
- when it last changed
- nearby pending changes already known

### 3) Sticky-exception test card

This card must answer explicitly:

- will any local exception remain after this action?
- will later parent changes affect this subject again?
- does any hidden remembered value survive behind the scenes?

Allowed verdicts:

- `true rejoin`
- `partial rejoin with remaining exception`
- `cannot rejoin from this surface`
- `blocked until config / cohort review`

### 4) Future-reaction card

Show one concrete simulation:

- if the parent default changes tomorrow, what happens to this subject?
- if the cohort splits, does this subject follow the parent or stay pinned?

### 5) Rejoin receipt preview

Preview the receipt sentence that will survive:

- `this subject now truly inherits`
- `this subject still carries a local exception`
- `this subject is pinned by a stronger plane`

### 6) Commit boundary

End with one clear action:

- `rejoin inheritance`
- `keep explicit override`
- `review stronger plane`
- `blocked`

## Rules

### Rule 1 — neutral labels must not lie

`Default`, `Auto`, `None`, or a cleared field must not imply inheritance unless future parent changes will truly flow through.

### Rule 2 — future reaction must be demonstrated

The page must simulate at least one future parent change to prove whether inheritance has really resumed.

### Rule 3 — hidden remembered overrides are forbidden

AnonSync must not preserve a dormant local exception that still wins later while pretending the subject returned to default.

## Acceptance criteria

A later operator can:

- tell whether the subject truly rejoined inheritance
- tell whether a hidden local exception remains
- tell how a later parent change will affect the subject
- preserve a receipt proving that `return to default` really meant what it said
