# Existing tree evidence page — share ID, lineage hints, and collision classes interface spec

## Purpose

The archive already has byte-witness, reuse, path continuity, and destination-world doctrine.
What still lacked one everyday page was the evidence page for the operator question:

> what exactly do we know about the target tree that makes it look like the same subject, a merge candidate, a duplicate namespace, or the wrong tree entirely?

This page exists so `.sync/ID`, non-empty-tree inspection, remembered roots, and collision classes stop hiding in warnings, support notes, or later repair ritual.

## Core decision

Every bind-outcome review that touches an existing or ambiguous target tree should expose one first-class **Existing tree evidence** page.

That page owns the current local evidence about the tree before commitment.

## Fixed page order

1. **Target identity strip**
2. **Same-subject evidence**
3. **Existing-tree shape**
4. **Collision classes**
5. **Missing or weak evidence**
6. **Next best evidence action**

### 1) Target identity strip

Show:

- target path
- selected world and bind lane
- current branch draft
- strongest current evidence class

### 2) Same-subject evidence

Show all currently known evidence families, such as:

- `same-share-id-present`
- `same-artifact-already-bound-elsewhere-on-seat`
- `remembered-root-match`
- `name-only-similarity`
- `hash-sample-match`
- `encrypted-empty-required`
- `no-same-subject-evidence`

The page must separate hard identity evidence from weak recognition hints.

### 3) Existing-tree shape

Show:

- target emptiness class (`empty`, `non-empty-small`, `non-empty-large`, `unreadable`, `unknown`)
- whether hidden service material is present
- whether the tree already contains other sync-managed evidence
- whether the tree shape suggests intended continuation, broad merge, or risky unrelated material

### 4) Collision classes

Classify every observed collision as one or more of:

- `same-id-collision`
- `same-name-different-lineage`
- `default-root-sibling-risk`
- `non-empty-merge-candidate`
- `ciphertext-empty-lane-violation`
- `target-already-bound-to-other-artifact`

The page must make collision class explicit before commitment.

### 5) Missing or weak evidence

Show what the product still does **not** know, such as:

- no share ID readable here
- lineage hint only from basename
- hash proof not yet computed
- target tree too large for quick confidence
- ciphertext lane chosen but target not yet emptied

### 6) Next best evidence action

Allowed actions include:

- `Compute stronger equivalence proof`
- `Open merge consequence compare`
- `Choose different target`
- `Clear target for ciphertext landing`
- `Treat as deliberate fork`

## Main surface

A compact **Existing tree evidence** card should show:

- target path
- strongest hard evidence chip
- strongest collision class chip
- one next evidence action

## Detailed surface

The detailed page should provide four panes.

### Pane A — Hard identity evidence

Rows may include:

- share-ID result
- remembered-root relation
- currently bound same-artifact rows

### Pane B — Tree shape summary

Rows may include:

- emptiness class
- service-material presence
- broad file-count or shape buckets

### Pane C — Collision class summary

Rows may include:

- class
- why it matters
- strongest likely branch consequence

### Pane D — Missing proof and next actions

Rows may include:

- weak or absent proof
- cheapest next proving move
- blocked unsafe actions

## CLI parity

Minimum commands:

- `anonsync target-evidence show <review-id>`
- `anonsync target-evidence inspect <review-id> --path <path>`
- `anonsync target-evidence strengthen <review-id> --mode <mode>`

## Acceptance criteria

A user can:

- tell whether the target tree already proves same subject, weakly resembles it, or conflicts with it
- distinguish same-ID collision from ordinary non-empty merge
- see empty-only ciphertext violations before commit
- carry the evidence page into later bind, merge, or repair reviews
