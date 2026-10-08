# Byte posture page: visibility, bind, and materialization lattice interface spec

The archive already has share-local presence decomposition, arrival-template doctrine, placement suggestion, and file-availability surfaces.
What it still lacked was one ordinary page that answers the operator's most common question without bouncing between those deeper models:

> for this share on this seat, what is visible here now, what is actually bound here now, what bytes are really here now, and what would happen to later arrivals if I changed something?

This page exists because current Resilio docs still make the value of byte-posture language obvious while also showing how easily one `mode` selector can blur current-share truth and later-default truth.

## Page promise

The Byte posture page should make four answers adjacent and non-substitutable:

1. **current visibility**
2. **current local bind**
3. **current byte materialization**
4. **future default for later arrivals in scope**

The page may compress calm cases.
It may not fuse those answers back into one label such as `Selective`, `Connected`, or `Here`.

## Fixed page order

Every byte-posture page should render the same sections in the same order:

1. **Share and seat now**
2. **Current bind and path provenance**
3. **Current byte lattice**
4. **Future-arrival default in scope**
5. **Admissible transitions**
6. **Receipt promise**

### 1) Share and seat now

This section should show:

- share identity and acting seat
- whether the share is announced, suggested, claimed, hidden locally, or withdrawn
- whether the current page is about one current share, a family scope, or both
- whether any current mutation would touch the current share or only the later default

The operator should be able to answer: **what exactly is in scope here right now?**

### 2) Current bind and path provenance

This section should show:

- whether a local bind exists
- bound path if one exists
- path provenance (`reviewed`, `template-derived`, `operator-picked`, `collision-adjusted`, `restored`, `reattached`)
- any current collision or missing-path blocker

The operator should be able to answer: **is there a real local home for this share, and how did it get chosen?**

### 3) Current byte lattice

This section should show byte posture as a small explicit lattice rather than one badge.
At minimum it should distinguish:

- `names hidden`
- `announced only`
- `bound, no local bytes yet`
- `placeholder-visible`
- `partial local bytes`
- `full local bytes`

Optional compact client wording is fine.
Semantic collapse is not.

The section should also show:

- whether current fetch is possible now
- whether current serve value exists here
- whether current posture is pinned, evictable, or guarded by last-copy risk

The operator should be able to answer: **what bytes are actually here now, and what is merely visible?**

### 4) Future-arrival default in scope

This section should show:

- governed scope (`this share only`, `future linked arrivals`, `family scope`, or similar)
- future default (`announce-only`, `claim-review-required`, `bind-with-placeholders`, `bind-with-full-copy`, `encrypted-store`, or similar)
- default path template if one exists
- collision handling default
- explicit line saying whether the current share changes if this default changes

The operator should be able to answer: **what will happen next time, and is that separate from what is true for this share now?**

### 5) Admissible transitions

The page should expose explicit actions, not one overloaded mode toggle.
Examples:

- `Claim here`
- `Rebind path`
- `Materialize bytes`
- `Revert to placeholders`
- `Change future default only`
- `Pin current share as exception`
- `Open placement review`

Actions that would touch both current share and future default should say so explicitly and require review.

The operator should be able to answer: **what honest state change is actually being offered here?**

### 6) Receipt promise

This section should say what later evidence survives after apply.
A byte-posture receipt should preserve at least:

- share and seat
- previous versus resulting bind posture
- previous versus resulting byte posture
- previous versus resulting future default, if touched
- path provenance and collision facts reviewed
- whether the action touched `current only`, `future only`, or `both`

The operator should be able to answer: **what later evidence will prove what changed and what did not?**

## Compact row contract

A trustworthy compact row should preserve the following order:

1. share
2. current bind phrase
3. current byte phrase
4. future-default phrase
5. next honest action

Example:

```text
Photos-2026   bound:/srv/family/Photos-2026 (reviewed)   placeholders here   future: announce-only   Review
```

A dense client may abbreviate the phrases.
It may not omit one of the four truths.

## What this page must never imply

The page must never imply that:

- a later default is the same fact as the current share's posture
- a path template is the same fact as an adopted local bind
- placeholder visibility is the same fact as durable fetchability
- changing byte posture automatically changes authority or future defaults
- changing future defaults automatically rewrites the current share silently

## CLI/API projection expectation

A headless operator should be able to render the same semantics through one projection such as:

```text
anonsync byte-posture show --share photos-2026 --seat self --view review
```

The textual result should still preserve the same six-section order.
The page is not a luxury for rich clients.
It is the canonical answer for one ordinary operator question.

## Result

This page is how AnonSync borrows Resilio's excellent byte-posture instinct without cloning the weaker habit of letting one convenience selector quietly stand in for bind truth, materialization truth, and future-default truth all at once.
