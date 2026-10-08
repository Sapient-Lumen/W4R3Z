# Existing-bytes intake page: non-empty target, equivalence proof, and merge terms interface spec

## Purpose

`158` established the adopt/rebind/path-repair review and `198` established preseed reuse proof.
This document makes them concrete as one ordinary page.

The page exists to answer one ordinary operator question:

> if I point this incoming subject at these already-existing local bytes, are we attaching, reusing, merging, duplicating, or about to make a mess?

## Core decision

Every intake or reconnect flow that names an already-existing target path must render one first-class **Existing bytes intake** page.
That page is the semantic home of:

- target-path occupancy truth
- duplicate-risk and same-name collision truth
- reuse / equivalence evidence
- merge or winner terms
- resulting bind class and receipts

The page must not reduce non-empty targets to a single `Folder is not empty` warning.

## Primary page layout

The page always renders the same top-level regions in the same order:

1. intake subject and target strip
2. target occupancy card
3. equivalence and reuse card
4. duplicate-risk and collision card
5. merge / bind outcome preview
6. recent bind receipts
7. expert evidence drawer

### 1) Intake subject and target strip

The strip shows:

- subject or share name
- proposed target path
- current target occupancy verdict
- strongest honest outcome preview
- next-honest-action button

Allowed occupancy verdicts:

- `empty target`
- `non-empty, likely intended continuation`
- `non-empty, merge candidate`
- `non-empty, duplicate risk`
- `non-empty, blocked mixed material`

### 2) Target occupancy card

Show:

- proposed target path
- whether the path is the remembered path, default suggestion, or operator-picked path
- whether contents are empty, sparse, populated, or mixed with unrelated material
- whether a same-name sibling duplicate would be created elsewhere if this path is not chosen
- last bind receipt affecting this path, if any

This card should make `default folder suggestion` and `continuity repair target` visibly different.

### 3) Equivalence and reuse card

Show the strongest current evidence for reuse:

- announced only
- path-name resemblance only
- size / mtime resemblance
- sampled hash agreement
- full-hash agreement
- block-map reuse candidate

Also show:

- what further scan or hash work remains
- expected local read burden
- whether full re-download is currently expected or avoidable

### 4) Duplicate-risk and collision card

This card is mandatory whenever a same-name sibling or alternate default path is in play.
Show:

- whether a new sibling directory would be created
- whether the subject already appears elsewhere on this seat
- whether the candidate looks like an older bind, a divergent copy, or unrelated bytes
- exact reason for any blocked bind

The page must not let indexed-sibling creation appear as an innocent success state.

### 5) Merge / bind outcome preview

Before apply, show one of these explicit actions:

- `Attach to empty target`
- `Bind to intended continuation`
- `Merge with reviewed winner terms`
- `Reuse local bytes, verify in background`
- `Create deliberate sibling copy`
- `Stop and inspect another path`

Each preview row shows:

- resulting bind class
- whether local bytes are reused or replaced
- whether duplicate namespace remains afterward
- whether later proof work is still pending
- which receipt will be emitted

### 6) Recent bind receipts

Show recent intake and reconnect receipts with:

- subject
- target path
- bind class
- reuse proof strength
- duplicate-risk verdict
- actor
- timestamp

### 7) Expert evidence drawer

Hide raw compare logs, path-scan evidence, and low-level hash details behind an expert drawer.
Those details matter, but they should not replace the typed page verdict.

## Narrow-width behavior

In narrow width the page may compress compare tables, but it may not hide:

- target occupancy verdict
- strongest reuse proof
- duplicate-risk verdict
- exact bind outcome text

## Acceptance criteria

This spec is satisfied when:

- non-empty intake is explained as path continuity and byte equivalence work rather than generic warning text
- deliberate sibling duplication is visibly different from continuity repair
- reuse proof strength is public before commit rather than implied after the fact
- default-folder suggestion cannot silently override intended path continuity
- any committed action leaves a receipt naming whether the result was attach, merge, reuse, sibling copy, or blocked repair
