# Empty-target purge review page: delete-unknown posture, bootstrap assumption, and pre-seeded risk interface spec

## Purpose

This review appears when a default or subject posture would allow unknown-file deletion on a non-authority seat.
It exists to answer one ordinary question before commit:

> are we merely healing known divergence, or are we authorizing destructive purge of unknown local material because this target is assumed empty and subordinate?

## When this review must appear

Trigger this review when:

- `folder_defaults.delete_unknown_files` changes
- `sync_ro_delete_unknown_file` changes
- an RO target is being attached as empty / new
- the operator tries to reuse a pre-seeded or ambiguous target under a purge-capable posture

## Fixed page order

1. purge summary header
2. bootstrap assumption card
3. candidate unknown-material matrix
4. pre-seeded risk warning
5. approval footer

### 1) Purge summary header

Show:

- subject / seat / target path
- purge verdict (`not-enabled`, `empty-target-only`, `ambiguous`, `unsafe-for-preseeded`, `unknown`)
- strongest safe sentence
- stronger rejected sentence

### 2) Bootstrap assumption card

Publish clearly:

- whether the target is declared empty
- whether the target is observed empty right now
- whether the seat is RO / non-authority
- whether the posture comes from a default or subject-specific source
- whether proof is declaration-only or observation-backed

### 3) Candidate unknown-material matrix

Rows:

- stray local file
- stray local directory
- preexisting partial mirror
- preexisting full mirror
- ambiguous reused target

Columns:

- will be preserved
- may be deleted
- requires branch/export first
- proof confidence

### 4) Pre-seeded risk warning

This warning must quote the operational idea, in product language, that the posture is **not optimized for pre-seeded folders**.
It must refuse stronger language such as:

- `safe for any reused target`
- `harmless cleanup`
- `equivalent to normal overwrite healing`

### 5) Approval footer

Require explicit approval whenever the product lacks strong empty-target proof or detects preexisting material.

## Rules

### Rule 1 — empty-target purge is stronger than overwrite-heal

Deleting unknown local material is a different destructive class from restoring known source state.

### Rule 2 — pre-seeded caution is first-class

A one-line advanced-preferences footnote is not enough.

### Rule 3 — declared emptiness is weaker than owned-target proof

The review must publish which proof class it actually has.
