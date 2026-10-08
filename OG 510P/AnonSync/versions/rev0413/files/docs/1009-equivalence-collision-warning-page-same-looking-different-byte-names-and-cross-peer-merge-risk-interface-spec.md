# Equivalence collision warning page — same-looking different-byte names and cross-peer merge risk

## Purpose

Warn when names that appear separate or identical to humans collapse into one risky equivalence class across the reviewed cohort.

This page exists to answer:

- `which names are colliding?`
- `are they literally equal, canonically equal, or peer-rewritten into equality?`
- `what merge, conflict, or rewrite risk follows if we continue?`

## Required sections

### 1. Collision summary

Must show:

- all candidate names in the collision set
- rendered forms side by side
- raw-form difference indicator
- collision class (`case-only`, `Unicode-form`, `symbol-rewrite`, `length-truncate`, `mixed`)

### 2. Horizon impact

Must publish:

- which peers or surfaces would collide
- whether collision is present now or only on later arrival / reconnect / restore
- whether current peers already contain conflict artifacts or rewritten variants

### 3. Risk ladder

Must distinguish:

- visible `.Conflict` risk
- silent rewrite risk
- blocked sync risk
- rename replay ambiguity
- archive / restore ambiguity

### 4. Safe resolution options

Must offer:

- choose one surviving canonical name
- export / branch one candidate out of band
- keep both only by widening their visible difference
- defer until missing horizon facts are gathered

### 5. Strongest safe sentence

Examples:

- `These names are not safely distinct across the reviewed cohort.`
- `The candidates differ in raw form, but at least one peer horizon would collapse them into one identity class.`

### 6. Blocked stronger sentence

Examples:

- `Both names can safely coexist because they currently appear separately on this seat.`
- `A visible difference to the human eye guarantees portable distinctness.`

## Interaction rules

- collision members must be copyable/exportable with both rendered and raw-form evidence
- the page must keep the reviewed peer horizon visible while the operator resolves the set
- any destructive resolution path must link to the existing salvage/repair family

## Receipt obligations

Any receipt derived from this page must preserve:

- full collision member set
- collision class
- reviewed horizon
- winning resolution path
- blocked stronger sentence
