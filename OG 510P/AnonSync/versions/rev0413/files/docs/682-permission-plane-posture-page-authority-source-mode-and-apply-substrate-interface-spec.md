# Permission-plane posture page: authority source, mode, and apply substrate interface spec

## Purpose

This page exists because `sync permissions`, `preserve ACLs`, `keep owner`, `same access`, and `portable permissions` are not the same truth.
A subject can be carrying permission meaning, applying it locally, re-inheriting locally instead, deferring application until a later compatible substrate, or not treating permissions as part of the synchronized meaning plane at all.

The page must let an operator answer one blunt question without article archaeology:

> what permission contract is active for this subject right now, and what is the strongest honest sentence the product can say on this seat?

## Core decision

AnonSync should make **permission-plane posture** first-class.
Every subject that can preserve or apply file permissions must publish, in one stable object:

- whether permissions are in scope at all
- whether the active mode is preserve, preserve-plus-owner, local re-inheritance, portable subset, or no-sync
- whether a reference authority exists and who it is
- whether this seat can apply the plane natively, defer it, or only carry it onward
- whether permission differences participate in divergence detection for this subject
- the strongest safe claim sentence after all those facts are considered together

## Fixed review order

Every permission-plane posture page should render the same sections in the same order:

1. **Mode now**
2. **Authority basis**
3. **Apply substrate**
4. **Privilege floor**
5. **Detection participation**
6. **Claim ceiling**

### 1) Mode now

Show:

- current mode: `none`, `portable-subset`, `full-preserve`, `preserve-plus-owner`, `local-reinherit`, `deferred-apply`, `unknown`
- exact policy source: template, subject override, imported legacy, or runtime fallback
- whether mode is mutable live, mutable only by recreation, or locked for the subject epoch

The operator must be able to answer: **what kind of permission contract is active here?**

### 2) Authority basis

Show:

- whether authority is `single-reference`, `current-writer-merge`, `seed-authority`, `local-only`, or `none`
- current reference seat if any
- whether authority is stable, degraded, missing, or disputed
- whether pre-seeded RW disagreement exists

The operator must be able to answer: **whose permission meaning is supposed to win?**

### 3) Apply substrate

Show:

- current seat substrate class
- whether the seat can apply permissions natively now
- whether it preserves them for later application on another substrate
- whether the active mode intentionally re-inherits from the local parent instead of applying remote permission state

The operator must be able to answer: **are permissions being applied here, carried onward, or rewritten locally?**

### 4) Privilege floor

Show:

- required local privilege grade for the active mode
- current process privilege grade
- missing rights if any
- whether the gap affects preservation, application, owner/group mutation, or only advanced cases

The operator must be able to answer: **does this seat actually have enough authority to do what the row claims?**

### 5) Detection participation

Show:

- whether permission differences are part of `needs-sync` comparison for this subject
- whether timestamps/size/ctime are also in scope
- whether disabling or narrowing this plane changes only final apply semantics or also comparison behavior

The operator must be able to answer: **can permission drift trigger sync work here?**

### 6) Claim ceiling

Show:

- strongest safe sentence
- stronger forbidden sentence
- evidence basis timestamp
- main uncertainty if present

Examples of safe sentences:

- `This subject preserves file permissions and owner/group from reference seat home-nas.`
- `This seat carries permission meaning but cannot apply it until the subject lands on a compatible substrate.`
- `This subject intentionally re-inherits local parent permissions on this seat.`
- `Permission differences do not participate in sync comparison for this subject.`

## Main card

The subject workspace should expose a **Permission plane** card with:

- current mode chip
- authority chip
- apply-substrate chip
- privilege chip
- compare-participation chip
- `Inspect permission contract`

## Detailed page

### Pane A — Mode summary

Columns:

- field
- value
- basis
- mutability
- confidence

### Pane B — Authority lineage

Show:

- reference seat or merge basis
- last authority proof
- current disputes
- next required review if authority is missing or degraded

### Pane C — Apply substrate and privilege

Show:

- substrate compatibility
- local privilege grade
- deferred-apply or local-reinherit explanation
- blocked rights

### Pane D — Detection participation

Show:

- which file attributes are in the sync-decision equation
- what changes if permission sync is disabled or narrowed
- whether current drift is comparison-only, apply-only, or both

### Pane E — Claim language

Show safe phrases and forbidden phrases.

## CLI parity

Minimum commands:

- `anonsync permissions show <subject>`
- `anonsync permissions explain <subject> --seat <seat>`
- `anonsync permissions claim-ceiling <subject>`

## Acceptance criteria

A user can:

- tell whether permissions are in scope right now
- see whether a reference authority is in force
- distinguish native apply, deferred apply, and local re-inheritance
- see whether permission drift can trigger sync work
- know the strongest sentence the product may safely say afterward
