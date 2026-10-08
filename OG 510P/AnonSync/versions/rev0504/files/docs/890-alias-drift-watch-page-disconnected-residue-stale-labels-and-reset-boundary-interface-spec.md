# Alias drift watch page: disconnected residue, stale labels, and reset boundary interface spec

## Purpose

This page exists because current naming truth can decay:

> which labels around this subject are now stale, residue-only, audience-misaligned, or no longer attached to active continuity?

## Core decision

Every subject whose labels can survive disconnect, deactivation, issuance drift, or local cleanup must render one first-class **Alias drift watch** page.

## Fixed page order

1. active truth strip
2. drifted-label inventory
3. residue classification matrix
4. reset and cleanup options
5. drift receipt rail

### 1) Active truth strip

Show:

- canonical active title
- active local alias if any
- current default recipient label if any
- one sentence saying whether the naming world is aligned or drifted

### 2) Drifted-label inventory

List each stale or divergent label with:

- label text
- plane
- current visibility audience
- drift class
- how it became stale
- whether it is still recoverable, resettable, or only historically relevant

### 3) Residue classification matrix

Supported classes should include at minimum:

- `older but still valid artifact label`
- `disconnected local alias residue`
- `superseded template`
- `stale disk-path memory`
- `historical only`
- `misleading and requires immediate review`

### 4) Reset and cleanup options

Actions may include:

- `reset stale local alias`
- `keep as historical only`
- `reissue artifacts with aligned label`
- `promote template to canonical retitle review`
- `do nothing; watch`

Each option must say which drift classes it clears and which it does not.

### 5) Drift receipt rail

Link recent resets, reissues, retitles, or cleanup receipts.

## Rules

### Rule 1 — residue must be reviewable without mutation

The operator must be able to inspect stale labels without being forced immediately into cleanup.

### Rule 2 — historical visibility is not active truth

A visible old label may remain historically relevant while no longer being the active shared name.

### Rule 3 — reset scope stays narrow

Resetting a stale local alias must not overclaim artifact cleanup or canonical subject retitle.

### Rule 4 — misleading residue gets urgency

If the product judges a stale label likely to mislead active operators or recipients, it must say so plainly.

## Acceptance criteria

A later operator can:

- enumerate stale and active labels separately
- tell how each stale label survived
- choose a cleanup/reset/reissue action with correct scope
- keep historical labels visible without mistaking them for current truth
