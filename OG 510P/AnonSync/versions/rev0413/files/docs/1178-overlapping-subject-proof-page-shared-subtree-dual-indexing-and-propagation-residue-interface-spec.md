# Overlapping-subject proof page: shared subtree, dual indexing, and propagation residue interface spec

## Purpose

After any serious overlap admission, a later operator must be able to answer:

> what exact overlap was admitted, what residue did it create, and what stronger claim did the product explicitly refuse to make?

This page exists so nested overlap does not dissolve into folklore.

## Core decision

Every serious overlap-topology mutation emits one first-class **Overlapping-subject proof** page.

The proof records:

- claim class
- subject pair
- seed-gap verdict
- dual-index verdict
- propagation residue
- strongest safe sentence
- stronger rejected sentence

## Fixed proof sections

1. header
2. overlap summary
3. seed and propagation evidence
4. indexing and rescan evidence
5. blocked stronger sentence
6. reopen conditions

### 1) Header

Show:

- proof id
- target scope
- operator / runtime label if known
- timestamp
- action class

### 2) Overlap summary

Show rows for:

- parent subject
- child subject
- overlap class
- permission floor met or not
- selective-sync eligibility basis

### 3) Seed and propagation evidence

Show:

- parent-only → child-only seed verdict
- child-only → parent-only propagation verdict
- direct vs indirect route explanation
- proof freshness

### 4) Indexing and rescan evidence

Show:

- child subtree indexing count
- child subtree rescan count
- heavy-load risk class
- origin seat or seats paying the overlap cost

### 5) Blocked stronger sentence

Examples:

- `Blocked stronger sentence: every peer that can see the child bytes can also seed the child subject.`
- `Blocked stronger sentence: this overlap behaves like one unified subject.`
- `Blocked stronger sentence: claiming the larger root is harmless because the interior subject is service-owned.`

### 6) Reopen conditions

Reopen automatically when:

- either subject flips into selective materialization
- parent or child permissions fall below the required floor
- the parent or child is disconnected and reattached elsewhere
- the interior ID boundary changes
- runtime restarts with a different admission source

## Rules

### Rule 1 — proofs must preserve seed-gap truth, not just requested topology

The proof records what direct seeding was actually available.

### Rule 2 — dual indexing evidence must record cost residue

A proof without cost residue is incomplete.

### Rule 3 — stronger blocked sentence is mandatory

The proof must retain the claim that the product explicitly refused to make.
