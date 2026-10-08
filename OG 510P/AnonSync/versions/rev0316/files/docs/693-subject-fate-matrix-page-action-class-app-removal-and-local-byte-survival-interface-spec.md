# Subject-fate matrix page: action class, app removal, and local-byte survival interface spec

## Purpose

Identity actions often affect more than one local subject class at once.
The operator needs one matrix that answers:

> for each governed subject class on this seat, what happens in the app, what happens on disk, and what platform rule explains the difference?

## Core decision

AnonSync should publish **subject-fate matrix** as the proof-adjacent companion to identity-action review.
The matrix is not a generic checklist.
It is the typed local survival map for the current action.

## Columns

Every row should show:

1. subject class
2. current local presence
3. post-action governance state
4. post-action byte state
5. platform basis
6. recovery path

## Required rows

The page must include any class currently present on the seat, such as:

- advanced-governed subject
- standard-governed subject
- landed local bytes without future governance
- imported / copied payload branch
- unknown / mixed class requiring manual inspection

## Value vocabulary

### Current local presence

Use:

- `present-and-governed`
- `present-branch-only`
- `listed-not-materialized`
- `not-present`
- `unknown`

### Post-action governance state

Use:

- `unchanged`
- `removed-from-app`
- `replaced-by-successor`
- `manual-reclaim-required`
- `copied-in`
- `unknown`

### Post-action byte state

Use:

- `bytes-stay-local`
- `bytes-deleted-local`
- `bytes-unchanged-but-ungoverned`
- `bytes-replaced`
- `unknown`

### Platform basis

Use short typed reasons:

- `desktop-nondestructive`
- `mobile-delete-cliff`
- `subject-class-specific`
- `receipt-only-evidence`
- `unknown`

### Recovery path

Use:

- `none-needed`
- `relink-later`
- `manual-reimport`
- `recover-from-other-seat`
- `preserve-before-action`
- `unknown`

## Main view

The matrix should default to one dense table plus one plain-language summary sentence.

Example summary sentence:

`On this seat, Advanced subjects leave governance under the requested identity action; desktop bytes remain local, but this platform class would delete governed bytes if the same action ran on mobile.`

## Rules

### Rule 1 — app removal and byte removal must never share one unlabeled cell

Governance loss and byte deletion are different fates and must always have different columns.

### Rule 2 — platform basis must be public

If the local-byte fate changes because of platform architecture, the matrix must say so directly.

### Rule 3 — recovery path must be typed, not implied

The matrix must never assume that `still on disk` means `easy to recover` without naming the actual recovery path.

### Rule 4 — mixed class must stay inspectable

If the product cannot classify a row cleanly, it must show `unknown / mixed class requiring manual inspection` rather than bluffing.

## Acceptance criteria

A later operator can:

- see class-by-class fallout for the pending identity action
- distinguish governance loss from byte deletion
- understand whether platform architecture changes the result
- know the next recovery rung for each affected row
