# Action claim review page — requested verb, effective claim, and forbidden overstatement interface spec

## Purpose

The archive already had strong severance, delete, and revocation doctrine.
What it still lacked was one review surface that answers a more social but still operational question cleanly:

> after this action runs, what exact sentence is the product willing to stand behind, and which stronger sentence must it actively refuse?

Current official Resilio docs make this seam concrete.
They still distinguish future-update revocation from byte recall, local disconnect from remote retainer loss, local unlink from remote unlink, and global delete from total residue disappearance.
That operational candor is good.
The missing part is one review page that owns the claim boundary before and after commit.

## Core decision

AnonSync should treat every high-consequence departure, revocation, deletion, or containment action as an **action claim review**, not just an action preview.

Every review must separate four things:

- requested operator verb
- effective action class
- strongest safe post-action statement
- stronger forbidden statement

The operator should never have to infer the safe sentence from menu wording alone.

## Why this matters

A successful button press does not automatically earn a strong sentence.
The reviewed page must explicitly answer:

- what action actually executed
- what that action proved
- what it did not prove
- what phrase the product will refuse to publish or suggest

## Fixed review order

Every action claim review should render the same sections in the same order:

1. **Requested sentence**
2. **Effective action class**
3. **Safe statement**
4. **Forbidden overstatements**
5. **Residual basis**
6. **Commit or escalate**

### 1) Requested sentence

Capture:

- object under action
- operator's requested wording in plain language
- intended audience (`self`, `teammate`, `admin`, `external recipient`)
- whether the operator is trying to claim local change, future-update cutoff, byte deletion, or incident containment

### 2) Effective action class

Show:

- matched action class
- confidence in the classification
- why the action class is narrower or broader than the requested wording
- what proof basis supports the class

Representative classes include:

- `row hidden`
- `seat-local disconnect`
- `linked-cohort removal`
- `future-updates revoked`
- `local bytes evicted to stubs`
- `participating-retainer delete`
- `local unlink only`
- `rotation initiated, not yet complete`

### 3) Safe statement

Render one product-backed sentence in large type, for example:

- `Future updates to this peer are revoked; already-landed files remain.`
- `This seat is disconnected here; local bytes remain on disk.`
- `This file was deleted from participating retainers and archived by policy.`
- `This device was unlinked locally; other devices were not remotely unlinked.`
- `Rotation has started; containment is not yet complete.`

This sentence must be copyable and exportable.

### 4) Forbidden overstatements

Show a short list of stronger sentences the product refuses to endorse, for example:

- `Access is completely gone everywhere.`
- `The data no longer exists.`
- `That device cannot come back.`
- `The incident is contained.`

Each forbidden sentence must show the blocking reason.

### 5) Residual basis

Show the state planes that limit the claim:

- local bytes
- linked cohort effect
- external retainer possibility
- history / archive residue
- return trigger
- unresolved escalation work

### 6) Commit or escalate

Offer only safe actions:

- `Apply with safe statement`
- `Choose weaker wording`
- `Choose stronger action`
- `Open residual matrix`
- `Open escalation review`
- `Cancel`

## Main surface

The main page should have:

- a verdict banner: `Requested sentence overclaims; use the reviewed sentence below.`
- a claim-grade chip: `local`, `future-update`, `linked-cohort`, `authorized-retainer`, `rotation-incomplete`
- a publication chip: `safe to paste`, `safe only with caveat`, `not yet publishable`
- a mandatory diff card comparing requested wording to approved wording

## Detailed panes

### Pane A — Claim ladder compare

Columns:

- candidate sentence
- supported?
- support basis
- contradiction basis
- audience fit

### Pane B — Residual blockers

List:

- landed bytes outside recall
- non-linked retainers still possible
- rows that may reappear
- unresolved rotation or cleanup tasks

### Pane C — Evidence links

Show the evidence basis used to approve or refuse a claim:

- action type
- rights basis
- retainer graph
- retention policy
- incident posture

### Pane D — Commit guard

Require an explicit acknowledgment when the requested sentence is broader than the safe sentence.

## CLI parity

Minimum commands:

- `anonsync claim review <object>`
- `anonsync claim review <object> --requested "their access is gone"`
- `anonsync claim review <object> --audience external`

## Acceptance criteria

This spec is satisfied when:

- every serious action yields a safe sentence distinct from raw button wording
- stronger unsupported sentences are named explicitly rather than implied away
- residual scope remains adjacent to the approved sentence
- the operator can escalate to a stronger action when the desired sentence is not yet earned
