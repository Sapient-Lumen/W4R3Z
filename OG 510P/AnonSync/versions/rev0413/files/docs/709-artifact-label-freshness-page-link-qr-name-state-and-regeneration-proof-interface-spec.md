# Artifact label freshness page: link, QR, name state, and regeneration proof interface spec

## Purpose

This page exists because outward artifacts can look current while actually carrying an older label state.
The page must answer:

> does the currently visible link / QR / outward alias still reflect the present name state, or am I about to hand out a stale artifact?

## Core decision

Every serious sync product must own one first-class **Artifact label freshness** page.
That page publishes the freshness ladder behind every outwardly named artifact.

## Fixed page order

1. artifact strip
2. current name-state basis
3. artifact-generation evidence
4. freshness verdict
5. safe actions and non-actions
6. residual uncertainty and receipts

### 1) Artifact strip

Show:

- artifact kind (`link`, `qr`, `copied invite`, `other`)
- subject and seat
- currently shown label text
- current strongest freshness verdict
- claim ceiling

### 2) Current name-state basis

Show:

- current relevant name planes
- which plane the artifact is supposed to reflect
- whether the plane changed after artifact generation

### 3) Artifact-generation evidence

Show:

- when the artifact was generated or last refreshed
- whether the visible artifact view was regenerated after the last label mutation
- proof class: `freshly-generated`, `generated-before-rename`, `view-not-refreshed`, `unknown`

### 4) Freshness verdict

Show one of:

- `fresh`
- `fresh for local preview only`
- `stale after rename`
- `regeneration required`
- `reissue required`
- `unknown`

### 5) Safe actions and non-actions

Show:

- `copy/use now`
- `regenerate view first`
- `reissue outward artifact`
- `reset local residue before export`
- `do not distribute`

### 6) Residual uncertainty and receipts

Show:

- missing proofs
- unresolved plane mismatches
- receipt refs
- one next honest action

## Rules

### Rule 1 — visible label is not freshness proof

The page must explicitly distinguish what is displayed now from what the artifact payload actually contains.

### Rule 2 — regeneration and reissue must not collapse

The page may not imply that refreshing a local view is the same thing as revoking/reissuing a previously shared outward artifact.

### Rule 3 — stale outward state must be named plainly

The page may not hide stale artifacts behind generic `rename applied` language.

## Success criteria

The page is successful only when a later operator can answer:

1. which name plane the artifact reflects
2. whether that plane changed after generation
3. what proof exists that the artifact was refreshed
4. whether copy/use is honest right now
5. what uncertainty still remains
