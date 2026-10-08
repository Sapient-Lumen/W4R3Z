# Linked-graph default arrival page: owner posture, disconnected mode, and manual read-only exception interface spec

## Purpose

This page exists when an operator is deciding whether identity linking is the right lane for future subject arrivals.
It answers one ordinary question:

> once this seat joins the graph, how will future folders arrive here by default, what authority do they imply, and what exceptions require leaving the linked-device lane entirely?

## When this page must appear

Trigger this page for:

- choosing default linked-device synchronization mode
- reviewing where future graph-visible folders will materialize
- any need for manual path selection on future arrivals
- any request for a read-only linked-device outcome

## Fixed page order

1. arrival posture header
2. mode and path card
3. authority and exception card
4. proof and limitation card
5. receipt/export rail

### 1) Arrival posture header

Show:

- seat / identity graph / current linked-device mode
- future-arrival verdict (`auto-visible disconnected`, `auto-visible selective`, `auto-visible synced`, `manual-share only`, `unknown`)
- strongest safe sentence
- stronger rejected sentence

### 2) Mode and path card

Render rows for:

- default mode selected for new arrivals
- whether bytes materialize immediately or only after connect/hydration
- whether default-folder placement is automatic
- whether `Disconnected` is required for manual location choice
- platform caveat for Android simple-mode disabling when manual path choice is needed

### 3) Authority and exception card

Show consequences such as:

- linked-device lane defaults to owner-level posture for shared subjects
- source seat remains effectively full-data / synced from origin
- true RO exception is not available by ordinary linked-device arrival
- RO exception requires Standard-folder manual sharing with a Read Only key

### 4) Proof and limitation card

Possible rungs:

- `documented default only`
- `mode visibly configured`
- `manual-path branch chosen`
- `RO exception path reviewed`
- `first linked arrival witnessed`

### 5) Receipt/export rail

Offer:

- `Emit identity lineage receipt`
- `Open certificate takeover review`
- `Open identity-graph adoption contract sheet`

## Rules

### Rule 1 — auto-arrival and authority must remain separate

Showing folders automatically and granting owner-grade posture are different truths and both must be visible.

### Rule 2 — disconnected mode must publish its real purpose

It is a path-authorship branch, not a failure to sync.

### Rule 3 — read-only exceptions must stay explicit

The page must say when the operator must leave the linked graph lane and use a manual share instead.
