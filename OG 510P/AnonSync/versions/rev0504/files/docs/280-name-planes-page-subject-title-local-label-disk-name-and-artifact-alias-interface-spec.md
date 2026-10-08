# Name planes page: subject title, local label, disk name, and artifact alias interface spec

## Purpose

`182` established the general name-plane contract.
This document makes it concrete as one ordinary page.

The page exists to answer one ordinary operator question:

> what is this thing called in the product, on this seat, on disk, and in outward artifacts, and which of those names would actually change if I edit one now?

## Core decision

Every subject with more than one meaningful name plane must render one first-class **Name planes** page.
That page is the semantic home of:

- stable subject title
- local seat label
- on-disk basename on the active mount
- peer-visible alias when one exists
- outbound artifact / invite label
- naming receipts

The page must not compress those into one unlabeled `name` field.

## Primary page layout

The page always renders the same top-level regions in the same order:

1. current planes strip
2. stable subject card
3. local seat and disk card
4. outward-artifact naming card
5. propagation and ambiguity card
6. rename / relabel actions
7. recent naming receipts

### 1) Current planes strip

The strip shows:

- subject title
- current active local label
- current active disk basename
- current outward artifact label if any
- one next-honest-action button

If several planes match exactly, the page may display a calm `currently aligned` verdict.
If they diverge, it must display `multiple active name planes`.

### 2) Stable subject card

Show:

- stable subject title
- subject identity continuity note
- whether the title is global, family-wide, or still draft-local
- latest receipt that changed the stable title

This card answers `what is the durable semantic title of the shared thing?`

### 3) Local seat and disk card

Show:

- local UI/workbench label on this seat
- on-disk path basename on this mount
- full current path
- whether the label and disk basename intentionally diverge
- whether changing one would affect the other

The page must make `local label only` and `rename path here` visibly different actions.

### 4) Outward-artifact naming card

Show:

- current artifact or invite label template
- whether peers or recipients see that label today
- whether future artifacts will inherit it
- whether older artifacts still carry older labels
- whether a peer-visible alias exists separately

This card answers `what label will a new invite or outward artifact carry?`

### 5) Propagation and ambiguity card

This card is mandatory whenever at least two planes differ.
Show:

- who sees each plane
- whether the plane propagates to peers, future artifacts, or only this seat
- whether current divergence risks misleading continuity
- whether the edit should reopen path review, subject relabel review, or artifact reissue review

### 6) Rename / relabel actions

Before apply, render explicit actions such as:

- `Retitle subject`
- `Change local label only`
- `Rename disk path here`
- `Set peer-visible alias`
- `Reissue outward artifact with new label`
- `Reset local label to inherited default`

Each action row shows:

- changed planes
- unchanged planes
- audience / propagation scope
- whether older artifacts remain unchanged
- receipt class to be emitted

### 7) Recent naming receipts

Show recent naming mutations with:

- actor
- subject
- changed planes
- unchanged planes
- propagation scope
- whether any outward artifact was reissued
- timestamp

## Narrow-width behavior

In narrow width the page may stack sections, but it may not hide:

- stable subject title
- local label versus disk basename
- current outward-artifact label
- propagation scope of the pending action

## Acceptance criteria

This spec is satisfied when:

- an operator can answer all current active names from one page
- local relabel, disk rename, and artifact relabel are visibly different actions
- name-plane divergence stays declared instead of becoming support lore
- older outward artifacts do not silently impersonate newly relabeled ones
- every naming mutation leaves a receipt naming exactly which planes changed and which did not
