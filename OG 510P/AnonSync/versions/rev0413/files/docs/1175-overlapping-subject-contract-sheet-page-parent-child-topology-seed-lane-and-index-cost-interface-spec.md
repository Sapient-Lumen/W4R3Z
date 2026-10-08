# Overlapping-subject contract sheet page: parent-child topology, seed lane, and index cost interface spec

## Purpose

Before an operator admits a child subject inside a parent subject, expands a larger root over an existing subject, or reconnects a pre-populated descendant into an already-claimed tree, they need one ordinary page that answers:

> what overlap topology am I creating here, what subjects are distinct, who can seed whom, and which stronger sentence is still blocked?

This page exists so `nested share` never remains a scattered FAQ pattern.

## Core decision

Every serious overlap-affecting action must open one first-class **Overlapping-subject contract sheet**.

The sheet owns:

- overlap class
- parent subject
- child subject
- admission basis
- materialization posture
- seed graph summary
- dual-index cost
- strongest safe sentence
- stronger rejected sentence

## Fixed page order

1. overlap claim header
2. subject-boundary card
3. seed-lane card
4. materialization and eligibility card
5. overlap cost and residue card
6. proof ceiling and next-safe action rail

### 1) Overlap claim header

Show at minimum:

- target scope (`subject`, `parent-child pair`, `cohort`, `unknown`)
- requested overlap posture (`admit-child`, `expand-parent`, `reconnect-descendant`, `claim-home-root`, `other`)
- strongest safe sentence
- stronger rejected sentence
- evidence freshness

Example safe sentence:

- `This action would create two distinct subjects in one directory lineage; parent-only peers can still observe descendant bytes through the parent path, but they are not authoritative seeders for child-only peers.`

### 2) Subject-boundary card

Render rows for:

- parent subject identity
- child subject identity
- shared physical subtree
- claim relationship (`disjoint`, `overlapping`, `same-id blocked`, `contains-existing-subject`, `unknown`)
- authority floor (`both RW/Owner required`, `blocked`, `unknown`)

### 3) Seed-lane card

Separate these truths explicitly:

- parent↔parent seed lane
- child↔child seed lane
- parent-only → child-only seed lane
- child-only → parent-only shadow propagation lane
- route explanation

### 4) Materialization and eligibility card

Show:

- parent materialization posture
- child materialization posture
- overlap eligibility verdict
- selective-sync ceiling (`eligible only when disabled`, `not material`, `unknown`)
- non-empty reconnect requirement where relevant

### 5) Overlap cost and residue card

Show:

- indexing cost (`single`, `double-subtree`, `unknown`)
- rescan debt
- propagation residue
- interior-service-material conflict risk
- stronger blocked sentence if safety assumptions exceed evidence

### 6) Proof ceiling and next-safe action rail

Only show actions that preserve meaning, such as:

- `Open nested-share topology review`
- `Open overlap admission review`
- `Open overlapping-subject proof`
- `Emit overlapping-subject lineage receipt`

## Rules

### Rule 1 — shared path may not impersonate shared subject

A shared filesystem subtree is weaker than proof that all peers participate in one subject graph.

### Rule 2 — byte visibility and seed authority must stay separate

The page must keep `can later receive through the parent` separate from `is a seeder for the child subject now`.

### Rule 3 — selective posture and topology eligibility stay separate

A placeholder-capable or selectively materialized subtree is not automatically eligible for nested subject overlap.

### Rule 4 — strongest safe sentence must remain explicit

The page must say the most that can honestly be claimed now and preserve the stronger claim that is still blocked.
