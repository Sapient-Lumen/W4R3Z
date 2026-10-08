# Share-list row identity, materialization, route, and risk interface spec

## Purpose

The workbench spec already says the share list should not be just names and progress bars.
What it still lacked was a fixed row contract for the list operators actually live in all day.

This document answers one ordinary workbench question:

> when I glance at the share list, what minimum truth must one row preserve so I do not have to open every subject page just to know whether this share is merely visible, actually adopted, byte-rich or byte-thin, route-healthy or route-weird, and safe or unsafe for the next action I have in mind?

Current Resilio behavior makes this worth tightening.
Its docs show useful folder-state language, but real operator meaning still spreads across sync mode, permissions, peer list, folder preferences, route behavior, and troubleshooting pages.
AnonSync should do better at the first list row.

## Core decision

Each share row is a **decision row**, not a browse row.
It must keep seven truths adjacent:

1. what the share is
2. whether it is merely visible or locally adopted
3. how much byte presence exists locally now
4. what effective route posture matters right now
5. whether any risk or blocker changes the next safe action
6. what the safest next action is
7. where proof or deeper review lives

If the operator still has to combine one badge, one progress bar, one route icon, and one menu to reconstruct the answer, the row contract is too weak.

## Canonical row anatomy

Every major share row should render the following slots in a stable order:

1. **Subject slot**
2. **Local-presence slot**
3. **Byte-posture slot**
4. **Route slot**
5. **Risk / readiness slot**
6. **Primary-action slot**
7. **Review / proof slot**

### 1) Subject slot

Show:

- share title
- stable share ID or short handle
- optional lineage marker when this row is a derivative or successor

### 2) Local-presence slot

Show one honest phrase such as:

- `Incoming only`
- `Adopted at /srv/media`
- `Detached, path not bound`
- `Encrypted custody only`
- `Same-host child at /mnt/backup/media`

This slot answers:

> do I merely know about this share here, or has it been given a local home?

### 3) Byte-posture slot

Show one honest phrase such as:

- `No local bytes`
- `Placeholders only`
- `Mixed local bytes`
- `Full local copy`
- `Ciphertext only`

This slot answers:

> what byte reality exists here right now?

### 4) Route slot

Show:

- current effective route class
- current route anomaly when it matters

Good compact phrases:

- `LAN direct`
- `Overlay route`
- `Known-host direct`
- `Relay fallback`
- `Waiting source`

The row should not hide route truth behind a hover-only icon.

### 5) Risk / readiness slot

Show the strongest row-level warning or readiness verdict, for example:

- `Settled`
- `Lease active`
- `Degraded`
- `Blocked by policy`
- `Awaiting review`
- `Path drift`
- `Last-copy risk`

This slot answers:

> what fact would make the obvious action less safe than it first appears?

### 6) Primary-action slot

Render only the safest next honest verb for the row's current state.
Examples:

- `Adopt`
- `Open`
- `Inspect route`
- `Review drift`
- `Restore path`
- `Claim offer`
- `Repair continuity`

A row should not show a high-risk mutation inline merely because the same button existed in a safer state earlier.

### 7) Review / proof slot

Render:

- `Review`
- `Why`
- or a stable proof-chip jump when no broader review is needed

This slot is how dense tables stay honest without forcing every caution into the main button.

## Example rows

### Incoming but not yet adopted

```text
Family Photos     Incoming only           No local bytes      Overlay route   Awaiting review     Adopt          Review
```

### Adopted selective share on a healthy route

```text
Research Vault    Adopted at ~/Vault      Placeholders only   LAN direct      Settled             Open           Why
```

### Encrypted intermediary

```text
Nightly Backup    Encrypted custody only  Ciphertext only     Known-host      Settled             Inspect role   Why
```

### Route-weird share with transfer trouble

```text
Video Archive     Adopted at /srv/video   Mixed local bytes   Relay fallback  Degraded            Inspect route  Review
```

### Path drift / continuity issue

```text
Invoices          Detached, path missing   Full local copy    Waiting source   Path drift          Repair path    Review
```

## Row classes

### `browse-safe`

Use when the share is healthy enough that opening or inspecting it is the real next action.

### `adoption-decision`

Use when the share is visible here but path choice, byte posture, or authority effect still needs review.

### `repair-needed`

Use when path drift, continuity break, route break, or capability mismatch makes routine actions misleading.

### `risk-bearing`

Use when last-copy risk, destructive scope, settlement barrier, or temporary widening makes the ordinary action unsafe to fire inline.

## Inline action gate

### Inline actions allowed

Inline action is allowed only when all of the following are true:

- the row class is `browse-safe`
- the action does not widen authority
- the action does not destroy the last known usable copy
- the action does not require cross-object review

Examples:

- `Open`
- `Inspect`
- `Pin locally`
- `Fetch now`

### Escalate to review

The visible button should pivot to review when:

- adoption path choice matters
- authority or rights may widen
- the row carries last-copy or path-drift risk
- settlement / blocker proof affects the action
- the route answer is degraded enough that the operator needs explanation first

## Sorting and filtering rules

The share list should support at least these primary sort lenses:

- name
- review urgency
- local-presence class
- byte-posture class
- route anomaly
- risk / blocker class

And at least these filters:

- `incoming`
- `adopted`
- `ciphertext only`
- `degraded`
- `lease active`
- `blocked`
- `same-host derivative`

Sorting by transfer speed alone is not enough.
The list is for operational judgment, not ornament.

## Dense and narrow rules

On narrow surfaces the row may stack, but the first collapsed line must still preserve:

- local presence
- byte posture
- primary action

The second collapsed line must preserve:

- route posture
- strongest risk / readiness verdict

Bad collapsed row:

```text
Video Archive · Syncing
```

Good collapsed row:

```text
Adopted · Mixed local bytes · Inspect route
Relay fallback · Degraded
```

## Batch behavior

Batch actions may summarize rows only by compatible action class.

Good batch labels:

- `Adopt 3 incoming shares`
- `Inspect route on 4 degraded shares`
- `Review 2 drifted shares`

Bad batch labels:

- `Apply to selected`
- `Open all`
- `Fix selected`

If a mixed batch spans healthy and risk-bearing rows, the batch layer must split them visibly.

## Relationship to nearby specs

This spec is the share-list companion to:

- `38-operator-workbench-interface-spec.md`
- `94-availability-row-anatomy-and-review-pane-spec.md`
- `150-subject-workspace-and-review-stack-interface-spec.md`
- `227-route-evidence-latency-bottleneck-and-directness-explanation-interface-spec.md`

Those documents already define nearby truths.
This one fixes the everyday list row where those truths first need to survive contact with operator attention.
