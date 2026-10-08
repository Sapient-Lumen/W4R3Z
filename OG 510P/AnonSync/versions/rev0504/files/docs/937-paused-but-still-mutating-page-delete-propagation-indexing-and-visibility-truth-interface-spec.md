# Paused-but-still-mutating page: delete propagation, indexing, and visibility truth interface spec

## Purpose

This page appears whenever the visible state suggests `paused` or `not transferring`, but at least one other lane still mutates.
It exists to answer:

> what exactly is still changing even though transfer looks paused?

## Use cases

Open this page when any of these are true:

- payload lanes are blocked but deletions still propagate
- payload lanes are blocked but zero-byte / structural markers still propagate
- rescans or indexing continue
- the subject may still appear online or become visible on wake
- scheduler or share pause hides mixed behavior behind one badge

## Fixed page order

1. mixed-state header
2. surviving mutation lanes
3. non-mutating lanes
4. practical consequences
5. next-safe actions

### 1) Mixed-state header

Show:

- visible badge
- actual mixed verdict
- strongest safe sentence
- stronger rejected sentence

Example:

- `Payload transfer is paused, but deletions and indexing remain live; the product cannot claim a frozen subject.`

### 2) Surviving mutation lanes

For each surviving lane show:

- lane name
- why it survives
- whether it is immediate or deferred
- example consequence

Required examples to support:

- deletion propagation
- zero-byte / structural publication
- local detection and queue growth
- scheduled wake and later retry

### 3) Non-mutating lanes

Make it equally clear which lanes are actually blocked now.

### 4) Practical consequences

Render consequences such as:

- `A local delete may still be observed elsewhere.`
- `The queue can grow while payload remains blocked.`
- `Peers may currently see this subject as offline because the core is asleep.`
- `Resuming later may release already-detected work rather than discovering it from scratch.`

### 5) Next-safe actions

Offer only actions that reduce ambiguity, such as:

- `Open eligibility proof`
- `Convert to full runtime stop`
- `Narrow surviving mutation lanes`
- `Emit eligibility receipt`

## Rules

### Rule 1 — this page is not an error page

Mixed-state behavior can be intentional and must be explained without panic language.

### Rule 2 — do not overclaim frozen state

If any lane still mutates, the page must say so directly.

### Rule 3 — mixed-state truth must be portable

The explanation must be durable enough to stand in a receipt later.
