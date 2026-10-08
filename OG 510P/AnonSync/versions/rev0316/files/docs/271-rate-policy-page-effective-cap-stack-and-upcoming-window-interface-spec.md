# Rate policy page: effective cap stack, surviving activity truth, and upcoming window interface spec

## Purpose

`239` established the semantic contract for effective rate truth.
This document makes it concrete as one page.

The page exists to answer one ordinary operator question:

> what bandwidth posture is actually in force right now for this seat or subject, which layer won, what still proceeds despite the current cap or pause, and what changes next?

## Core decision

Every seat and every overridable subject must expose one first-class **Rate policy** page.
That page is the semantic home of:

- current effective upload/download caps
- WAN versus LAN posture
- winning policy layers
- surviving activities under pause/throttle
- next schedule transition
- mutation receipts

## Primary page layout

The page always renders the same top-level regions in the same order:

1. current verdict strip
2. effective-cap cards
3. winning-layer stack
4. surviving-activity card
5. upcoming-window timeline
6. change-policy drawer
7. recent receipts

### 1) Current verdict strip

The strip shows:

- scope (`seat` or one specific subject)
- one plain-language verdict
- current upload and download values
- next transition time if any

Example verdicts:

- `wan limited / lan unlimited`
- `wan and lan limited`
- `scheduled pause; deletions and indexing still continue`
- `subject override replaces seat default`
- `declared config locks current cap`

### 2) Effective-cap cards

Render separate cards for:

- WAN upload/download
- LAN upload/download
- whether caps are unlimited, throttled, or zero
- whether this scope inherits or overrides a broader scope

The page must never force LAN truth to piggyback invisibly on WAN truth.

### 3) Winning-layer stack

List policy layers in precedence order.
Typical rows:

- subject override
- seat global setting
- schedule window
- LAN exception
- declared config
- emergency safety clamp

Each row shows whether it changed the effective answer or was overridden.

### 4) Surviving-activity card

This card is mandatory whenever current caps are zero or heavily reduced.
Show whether these still proceed:

- deletions
- placeholder / namespace announcements
- indexing / rescans
- local hashing / verification
- zero-byte items
- peer discovery or route probing
- any remaining upload or download classes

`Paused` is not an adequate answer by itself.

### 5) Upcoming-window timeline

Show:

- next transition time
- next cap values
- whether the change is schedule-derived or manually set
- what activities will still survive then
- whether the transition affects just one subject or the whole seat

### 6) Change-policy drawer

Mutating controls may live in a drawer or side sheet, but the consequence preview must always show:

- old effective answer
- proposed new effective answer
- which layer will win after apply
- what surviving activity truth changes
- whether the change is temporary, scheduled, or durable

### 7) Recent receipts

Show recent mutations and scheduled state changes with:

- actor
- scope
- winning layer
- old caps
- new caps
- changed surviving-activity posture
- linked detail receipt

## Narrow-width behavior

In narrow width the page may collapse charts/timelines, but it may not hide:

- current WAN/LAN caps
- winning layer
- surviving activity truth
- next transition

## Acceptance criteria

This spec is satisfied when:

- the operator can read current WAN and LAN truth from one page
- `paused` never hides the activities that still proceed
- the page can say which layer produced the current answer
- schedule transitions are visible before they happen
- any mutation leaves a receipt that names the winning layer and changed side effects
