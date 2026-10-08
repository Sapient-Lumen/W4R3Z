# Non-authority convergence contract sheet page: seat role, heal posture, purge posture, and survivor truth interface spec

## Purpose

Before an operator enables overwrite healing, inherits a destructive default, attaches an encrypted custody seat, or tries to explain why local work did not publish, they need one ordinary page that answers:

> what authority class does this seat have here, what convergence posture is active, what local divergence classes will suspend versus auto-heal, and what survivors can remain on disk?

This page exists so `Read Only` or `Overwrite any changed files` do not remain dangerously over-compressed labels.

## Core decision

Every serious non-authority subject / seat pair must open one first-class **Non-authority convergence contract sheet**.

The sheet owns:

- seat authority class
- posture origin
- current heal posture
- current purge posture
- divergence-class fate matrix
- survivor map
- proof rung
- strongest safe sentence
- stronger rejected sentence

## Fixed page order

1. convergence claim header
2. seat and origin card
3. divergence fate matrix
4. purge and bootstrap card
5. proof card
6. claim ceiling and next-safe action rail

### 1) Convergence claim header

Show at minimum:

- subject / seat / runtime name
- authority class (`owner`, `rw`, `ro`, `encrypted-ro`, `default-derived-ro`, `unknown`)
- posture origin (`subject-setting`, `default-setting`, `seat-class hardwire`, `unknown`)
- convergence verdict (`suspends-on-local-change`, `source-heal-enabled`, `forced-source-heal`, `empty-target-purge-enabled`, `mixed`, `unknown`)
- strongest safe sentence
- stronger rejected sentence
- evidence freshness

Example safe sentence:

- `This seat cannot author shared truth for this subject; edited and deleted items may be healed from source, while added local items may still survive only locally.`

### 2) Seat and origin card

Render rows for:

- permission / authority class
- seat type
- whether Selective Sync is allowed
- whether encrypted custody rules apply
- whether this posture is default-derived or subject-specific
- whether empty-target-only purge posture exists

### 3) Divergence fate matrix

Rows must include at least:

- local content edit
- local delete
- local rename
- new local file
- unknown local file in empty target
- unknown local file in pre-seeded target

Columns:

- publishes to others
- suspends further update
- auto-heals from source
- remains local-only
- duplicates / re-downloads old path
- purge risk
- confidence grade

### 4) Purge and bootstrap card

Separate these truths explicitly:

- `overwrite-heal posture`
- `delete-unknown posture`
- `empty-target bootstrap assumption`
- `pre-seeded caution`

The page must never flatten `heal` and `purge` into the same setting family.

### 5) Proof card

Show the current proof rung:

- `documented behavior only`
- `saved default`
- `subject-level option active`
- `seat-class hardwire documented`
- `runtime behavior witnessed`

### 6) Claim ceiling and next-safe action rail

Only show actions that preserve meaning, such as:

- `Open read-only divergence review`
- `Open empty-target purge review`
- `Open forced source-heal proof`
- `Emit non-authority convergence receipt`

## Rules

### Rule 1 — seat class is not optional context

The page must not hide whether this is ordinary RO, default-derived RO, or encrypted custody.

### Rule 2 — heal and purge are different verbs

Auto-reverting known files and deleting unknown files are different destructive classes and must remain separate.

### Rule 3 — survivor truth is first-class

`Healed` is incomplete unless the operator can also see what stays stranded locally.

### Rule 4 — the page must refuse stronger language it cannot prove

Blocked examples:

- `all divergence is reconciled`
- `local drift is harmless`
- `this target is safe to clean`
