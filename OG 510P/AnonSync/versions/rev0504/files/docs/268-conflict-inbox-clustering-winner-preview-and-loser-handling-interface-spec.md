# Conflict inbox, clustering, winner preview, and loser-handling interface spec

## Purpose

The archive already has conflict objects and conflict-adjudication doctrine.
What it still lacked was a fixed workbench surface for the moment conflicts accumulate into an operator queue.

This document answers one ordinary but dangerous question:

> when several conflicts exist, what inbox lets me tell which ones are safe to defer, which ones are similar enough to batch-review, which ones demand path/portability reasoning, and exactly what will happen to the losing candidate before I click resolve?

Current sync products too often reduce conflicts to suffixes, badges, and filename archaeology.
AnonSync should instead give conflicts one honest inbox.

## Core decision

Conflicts must appear in a dedicated **Conflict inbox** with explicit clustering, explicit winner preview, and explicit loser-handling disclosure.

Each row must keep these truths adjacent:

1. what collided
2. what kind of conflict it is
3. whether a suggested winner exists
4. what loser handling is currently safest
5. whether batch treatment is allowed
6. what review depth is required

## Inbox layout

The page should have three persistent regions:

1. **Conflict cluster list**
2. **Candidate compare pane**
3. **Resolution review / receipt pane**

## Conflict row anatomy

Each row should render:

1. **Path / subject slot**
2. **Conflict-kind slot**
3. **Candidate-summary slot**
4. **Safety-class slot**
5. **Suggested-next-step slot**
6. **Review / receipts slot**

### Path / subject slot

Show the path and share plus any rename/mapping hint when names diverged.

### Conflict-kind slot

Use explicit kinds such as:

- `content divergence`
- `delete vs modify`
- `path collision`
- `case / unicode mapping`
- `capability mismatch`
- `authority / policy collision`

### Candidate-summary slot

Show a compact summary such as:

- `2 byte candidates`
- `delete vs live bytes`
- `3 path renderings`
- `winner suggestion available`
- `no safe winner suggested`

### Safety-class slot

Use one of:

- `inspect-safe`
- `compare-first`
- `portability-review`
- `policy-review`
- `blocked`

### Suggested-next-step slot

Render only the safest next honest verb:

- `Compare`
- `Review portability`
- `Review policy`
- `Accept suggested winner`
- `Open blocker`

### Review / receipts slot

Jump to:

- full candidate compare
- related history / rollback entries
- prior resolution receipts
- portability evidence

## Clustering rules

The inbox should allow clustering by:

- same share
- same directory subtree
- same conflict kind
- same portability class
- same suggested loser handling
- same originating incident window

But cluster badges must never erase per-row risk class.
A cluster may summarize, not flatten.

## Candidate compare contract

Opening a row should render candidates in a stable left/right or top/bottom order.
Use:

- incumbent / current-live candidate first
- incoming / competing candidate second
- additional candidates after that in stable provenance order

For each candidate show:

- rendered path
- source actor / seat
- capture / observation time
- content fingerprint summary
- portability concerns
- whether history or restore candidates already exist for it

## Fixed resolution-review order

The resolution pane should render sections in this order:

1. **Current conflict answer**
2. **Winner preview**
3. **Loser-handling disclosure**
4. **Scope and propagation truth**
5. **Blocked alternatives**
6. **Receipt promise**

### 1) Current conflict answer

One sentence first, for example:

- `This is a content divergence with one suggested winner and low loser-handling risk.`
- `This is a delete-vs-modify conflict; no safe automatic winner is suggested.`
- `This is a path portability collision and needs mapping review before any winner is honest.`

### 2) Winner preview

Show:

- candidate chosen or candidate suggested
- why that candidate is strongest
- any unresolved weakness in the suggestion

### 3) Loser-handling disclosure

Show one explicit loser outcome:

- `copy aside`
- `quarantine`
- `leave local only`
- `delete share-wide`
- `keep unresolved`

This section is mandatory.
Resolving a conflict without explicit loser handling is not acceptable.

### 4) Scope and propagation truth

Show:

- device-local vs share-visible consequences
- whether settlement review is required
- whether other seats will see the resolution as overwrite, rename, delete, or quarantine artifact

### 5) Blocked alternatives

Show why superficially similar actions are blocked.
Examples:

- `Batch resolve` blocked by mixed portability class
- `Delete loser share-wide` blocked by last-copy risk
- `Accept winner inline` blocked by policy collision

### 6) Receipt promise

Show the exact durable receipt / rollback object that will survive after apply.

## Batch rules

Batch resolution is allowed only when all rows in the batch share:

- the same conflict kind
- the same portability class
- the same loser-handling outcome
- no blocked or policy-review rows

Good batch labels:

- `Copy aside and keep incumbent on 5 content-divergence rows`
- `Open portability review for 3 path-collision rows`

Bad batch labels:

- `Resolve selected`
- `Use latest`
- `Delete losers`

## Deferral rules

The inbox should support deferral, but deferral must say what remains unsafe or unresolved.
Examples:

- `Deferred; no safe winner yet`
- `Deferred pending portability review`
- `Deferred; waiting stronger provenance`

A dismissed conflict may change queue presentation.
It must not rewrite the underlying case.

## Relationship to nearby specs

This spec is the inbox/page companion to:

- `72-conflict-adjudication-and-path-collision-review-spec.md`
- `48-history-conflict-and-rollback-provenance-spec.md`
- `174-restore-history-archive-and-share-safe-reintroduction-interface-spec.md`

Those documents already define conflict semantics and rollback consequences.
This one fixes the operator-facing inbox where conflict families should be read and resolved honestly.
