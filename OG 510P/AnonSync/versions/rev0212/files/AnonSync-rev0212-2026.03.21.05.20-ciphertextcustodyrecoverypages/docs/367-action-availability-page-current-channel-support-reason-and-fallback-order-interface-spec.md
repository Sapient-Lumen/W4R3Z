# Action availability page: current-channel support, reason, and fallback order interface spec

## Purpose

The archive already had abstract channel-parity doctrine.
This document makes the ordinary page concrete.

The page exists to answer one ordinary operator question:

> can I do this action here right now, and if not, is the blocker the current surface, product policy, my role, artifact health, or something broken in the client?

## Core decision

Every serious action that can appear from more than one projection must own one first-class **Action availability** page.
That page is the semantic home of:

- requested action identity
- current-channel support verdict
- blocker ownership
- typed fallback order
- continuity consequences
- recent availability receipts

The product must not let missing buttons, grayed-out verbs, or generic `not supported` text stand in for this page.

## Primary page layout

The page always renders the same top-level regions in the same order:

1. requested-action strip
2. current-channel support card
3. blocker-ownership card
4. fallback-order card
5. continuity-consequence card
6. recent availability receipts
7. expert details drawer

### 1) Requested-action strip

Show:

- action family
- subject and blast radius
- acting seat
- current channel
- strongest next-safe action

The strip should answer `what exact thing am I trying to do?`

### 2) Current-channel support card

Show one explicit support verdict:

- `fully supported here`
- `inspect only here`
- `supported through handoff`
- `blocked by policy here`
- `blocked by role or scope here`
- `surface degraded here`
- `artifact invalid or unsupported`

Also show:

- whether apply is possible here
- whether review is complete enough to hand off safely
- whether a richer sibling surface would change semantics or only execution channel

This card should answer `is the action truly available here, and at what strength?`

### 3) Blocker-ownership card

Show which family owns the current blocker:

- current surface mismatch
- browser or extension interference
- trust or session problem
- policy block
- role / capability ceiling
- artifact problem
- runtime health problem
- target-seat readiness problem

If more than one blocker exists, order them by first required fix.
The page must not flatten `browser hid the button` and `you are not allowed to do this` into one vague sentence.

### 4) Fallback-order card

Show the strongest honest continuation order, for example:

1. continue here
2. typed fallback in same surface
3. reviewed handoff to another local channel
4. broader repair before any continuation

Each fallback row must show:

- target channel or page
- whether the same review survives
- whether new trust or auth is required
- whether apply remains possible after handoff

### 5) Continuity-consequence card

Before any handoff or repair, show:

- whether the same subject/draft/gate survives
- whether channel change reopens broader review
- whether any receipts will fork
- whether the action becomes inspect-only on the target channel

This card should answer `if I leave this surface, am I still doing the same work?`

### 6) Recent availability receipts

Show recent receipts with:

- action family
- current channel
- support verdict shown at the time
- blocker owner
- fallback chosen
- resulting continuation or refusal

### 7) Expert details drawer

Hide raw client diagnostics, browser metadata, feature flags, and low-level render checks behind an expert drawer.
These details matter, but they are not the semantic center.

## Compact row contract

A trustworthy compact row should preserve the following order:

1. action phrase
2. support phrase
3. blocker-owner phrase
4. strongest next action

Example:

```text
Share Project Atlas   supported through handoff   current browser extension is suppressing the share affordance on local-web; role is sufficient   Open reviewed handoff
```

## Acceptance criteria

This spec is satisfied when:

- missing action and forbidden action are visibly different answers
- inspect-only, handoffable, and fully supported are visibly different answers
- typed fallback order is shown before the operator leaves the current surface
- the product emits a receipt for meaningful availability decisions rather than outsourcing memory to browser history or support lore
