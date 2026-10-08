# Equality posture page: effective compare plane and claim ceiling interface spec

## Purpose

This page exists because `same file`, `up to date`, and `needs sync` are not self-explanatory truths.
They depend on which property planes are currently in scope, which are merely optional, and which are only preserved or deferred.

The page must let an operator answer one blunt question without support-article archaeology:

> what exactly counts as the same object for this subject right now, and how strong is the claim the product is allowed to make?

## Core decision

AnonSync should make **Equality posture** first-class.
Every serious subject must publish, in one stable object:

- effective compare plane now
- optional planes in scope or out of scope
- proof ladder currently in force
- native-apply versus later-apply ceiling
- strongest safe sentence

## Fixed page order

Every equality-posture page should render the same sections in the same order:

1. **Sameness now**
2. **Property planes in scope**
3. **Proof ladder**
4. **Apply ceiling**
5. **Changed-basis history**
6. **Claim ceiling**

### 1) Sameness now

Show:

- subject and seat
- effective equality verdict family: `content-primary`, `content-plus-attrs`, `content-plus-attrs-plus-optional-planes`, `mixed`, `unknown`
- current compare trigger summary
- one next honest action

The operator must be able to answer: **what does `same` currently mean here?**

### 2) Property planes in scope

List the planes separately, not as one metadata blob:

- content
- name/path identity
- size
- modification time
- creation time
- execute bit
- permission plane
- xattr / stream plane
- platform-local decorations
- any subject-specific custom plane

For each plane show:

- `in compare plane`, `carried but not compared`, `optional and disabled`, `not synchronized`, `unknown`
- strongest basis
- operator-visible reason

The operator must be able to answer: **which properties are actually part of the judgment?**

### 3) Proof ladder

Show proof classes such as:

- `announced only`
- `quick-attribute quiet`
- `hash-equal`
- `content-equal but plane-divergent`
- `native parity proven`
- `later-apply parity only`
- `ambiguous`

The operator must be able to answer: **how much proof has actually been reached?**

### 4) Apply ceiling

Show:

- whether all in-scope planes can be applied natively on this seat
- whether some planes are only preserved for later compatible landing
- whether some planes narrow object fidelity on this seat
- whether the current seat is a native parity seat, later-apply seat, courier-only seat, or unknown

The operator must be able to answer: **can this seat honestly claim full parity, or only a narrower version?**

### 5) Changed-basis history

Show recent basis changes such as:

- creation time removed from compare plane
- permission plane disabled
- xattr/stream plane narrowed
- proof ladder changed from quick attributes to hashes

The operator must be able to answer: **what changed in the sameness contract recently?**

### 6) Claim ceiling

Show:

- strongest safe sentence
- stronger forbidden sentence
- evidence timestamp
- main uncertainty if present

Examples:

- `These objects are content-equal under the current compare plane, but permission parity is out of scope here.`
- `This seat can preserve the permission plane for later application, but cannot honestly claim native parity now.`
- `Quiet status here only reflects quick-attribute agreement; stronger hash proof is still pending.`

## Main card

The subject workspace should expose an **Equality posture** card with:

- compare-plane chip
- proof chip
- apply-ceiling chip
- `Inspect sameness basis`

## Rules

### Rule 1 — the compare plane must be enumerable

The page may not use only a single word such as `same`, `synced`, or `up to date` if the underlying property planes are not listed.

### Rule 2 — proof class and compare plane must stay adjacent

The page may not let `same` appear stronger than the proof class actually established.

### Rule 3 — later-apply ceilings must be explicit

The page may not imply native parity when a seat is only carrying or deferring a plane.

### Rule 4 — basis changes require history

If a toggle or profile change narrowed the compare plane, the page must preserve that fact.

## Acceptance criteria

A later operator can:

- identify what properties define sameness right now
- see which optional planes are in or out of scope
- know whether the claim is quick-attribute quiet, hash-proven, or fully parity-proven
- see whether this seat can apply all in-scope planes natively
- quote one honest sentence without support folklore
