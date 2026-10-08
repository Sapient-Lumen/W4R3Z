# Naming provenance sheet page: plane, origin, audience, and current render interface spec

## Purpose

`182` established the general name-plane doctrine.
`280` turned it into one ordinary current-state page.
This page adds one thing those earlier specs intentionally left lighter:

> for every visible serious label, where did it come from, who is it for, and is it still live truth or only local residue?

The page exists because a visible label without provenance is not trustworthy enough.

## Core decision

Every subject with more than one meaningful naming plane must render one first-class **Naming provenance sheet**.
That sheet owns:

- rendered current labels
- plane of each label
- audience of each label
- origin event or receipt
- current liveness or residue status
- best next naming action

## Fixed page order

1. current render strip
2. name-plane ledger
3. audience map
4. residue and staleness card
5. issuance lineage card
6. next-safe actions rail

### 1) Current render strip

Show at minimum:

- canonical subject title
- local seat alias on this seat if any
- disk basename on this mount if any
- current default outward label template if any
- strongest safe sentence

If all labels are aligned, the strip may say `all active name planes aligned`.
If they diverge, it must say `multiple active or remembered name planes`.

### 2) Name-plane ledger

Render one row per serious label with columns at minimum:

- rendered label
- plane (`canonical title`, `local alias`, `disk basename`, `recipient label template`, `issued artifact label`, `other`)
- origin (`inherited`, `local edit`, `issued artifact`, `filesystem rename`, `imported`, `residue`, `unknown`)
- audience (`this seat`, `selected seats`, `artifact recipients`, `all viewers`, `disk only`)
- live or residue status
- latest supporting receipt

### 3) Audience map

Show who actually sees each label now.
At minimum support these audiences:

- `only this seat`
- `this mount only`
- `future artifacts from this seat`
- `holders of older issued artifacts`
- `other active seats`
- `nobody active; residue only`

The page must make it impossible to mistake a local alias for a recipient-facing label.

### 4) Residue and staleness card

This card is mandatory whenever any label survives after disconnect, deactivation, or plane reset.
Show:

- residue label
- why it survived
- whether the underlying subject is still active here
- recommended cleanup action
- strongest forbidden stronger sentence

Example forbidden stronger sentence:

- `this is still the current shared name everywhere`

### 5) Issuance lineage card

If outward artifacts were issued with different labels, show:

- latest issued labels
- which artifact families carried them
- whether those artifacts remain valid
- whether later canonical/local changes did or did not alter those older artifacts

### 6) Next-safe actions rail

Only show actions that preserve plane truth, such as:

- `retitle canonical subject`
- `edit local alias only`
- `rename disk path here`
- `set default recipient label template`
- `inspect older issued labels`
- `reset stale local alias`

## Rules

### Rule 1 — every serious visible label needs plane and audience

The product must never show a serious label without stating what plane it belongs to and who sees it.

### Rule 2 — residue must badge itself

A stale alias that survived disconnect or deactivation must not impersonate live subject truth.

### Rule 3 — issued labels are not canonical by accident

A label carried by an already-issued artifact must remain attributable to that issuance event rather than to the subject globally.

### Rule 4 — actions must target planes, not generic `rename`

The page must not offer one ambiguous rename control that silently spans canonical title, local alias, disk path, and recipient label.

## Acceptance criteria

A later operator can:

- tell which visible name is canonical, local, disk-bound, or artifact-issued
- tell who actually sees each label now
- tell whether a label is active truth or residue
- tell whether older issued labels remain unchanged
- choose a next action without guessing which plane it edits
