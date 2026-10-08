# Blocker scope page: seat, subject, item, and hidden-state blast radius interface spec

## Purpose

Answer the ordinary question:

> how wide is this problem really, what remains unaffected, and which stronger operations should stay blocked until scope is proven smaller?

This page exists because operators often jump from a warning row directly to a heavy repair without knowing whether the issue is item-local, subject-local, seat-local, or continuity-bearing hidden-state damage.

## Core rule

Every non-trivial warning must be able to open a **blocker scope** page.
The page must preserve both:

1. **affected scope** — the smallest world currently proven affected
2. **claim ceiling** — what stronger statements are still blocked because scope may be wider than currently proven

## Required sections

### 1) Smallest proven affected world

Show one primary scope class:

- `item-only`
- `path-subset`
- `subject/share`
- `seat/runtime`
- `identity/control-plane`
- `storage-root`
- `unknown-wider-than-current-proof`

Also show why that class won.

### 2) Possible wider spillover

List any wider worlds that remain plausible but unproven:

- sibling items in same subject
- all selective/hydrated descendants
- all subjects on same seat
- peers that depend on the same chronology or helper state
- hidden service/control state shared by several subjects

### 3) Unaffected neighbors

Whenever possible, prove what is currently outside the blast radius:

- other subjects still healthy on the same seat
- sibling items with fresh proof of availability
- route/discovery functioning even if one subject is blocked
- local bytes intact even if chronology or continuity is invalid

### 4) Stronger actions now blocked

Show which actions stay blocked until scope shrinks or proof improves:

- destructive replay
- successor/cutover approval
- winner/loser language
- detach / rebuild / branch promotion
- cohort-wide maintenance claims

### 5) Scope-tightening probes

Offer less-destructive scope probes first:

- inspect peer/item evidence
- inspect chronology evidence
- inspect control-spine integrity
- inspect source presence
- inspect storage-floor / resource evidence

## View grammar

A good scope summary line reads like:

- `Proven affected: this subject only · wider continuity spillover unproven`
- `Proven affected: seat-local load pressure · no subject corruption proven`
- `Proven affected: item set lacking source peers · seat remains healthy`
- `Proven affected: chronology invalid across peer pair · winner claims blocked beyond item subset`

## Data model

- `blocker_scope_id`
- `warning_id`
- `smallest_proven_scope_kind`
- `smallest_proven_scope_ref`
- `possible_wider_scopes[]`
- `unaffected_neighbors[]`
- `blocked_stronger_actions[]`
- `scope_probe_options[]`
- `claim_ceiling_summary`

## Failure this page prevents

Without this page, one subject-local warning can trigger seat-wide panic, or one seat-local load condition can provoke continuity-destroying repair.

AnonSync should instead force the product to state the smallest proven affected world and the stronger actions still blocked by uncertainty.
