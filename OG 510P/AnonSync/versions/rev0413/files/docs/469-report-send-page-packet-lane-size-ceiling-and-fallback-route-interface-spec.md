# Report send page: packet lane, size ceiling, and fallback route interface spec

## Purpose

This page answers:

> what exact packet is about to leave this seat, by what route, under what size/transport ceiling, and what fallback route is honest if the first send lane fails?

The page exists because `Include logs`, `attach file`, `upload link`, `mobile hidden logs`, and `send to forum` are not the same transport contract.

## Core rule

Every outward diagnostic send must expose one first-class **Report send** page before commit.
That page owns:

- packet membership
- send route
- route-specific ceilings
- fallback route
- send completion proof

## Primary layout

The page always renders the same regions:

1. send verdict
2. packet membership card
3. route and size-ceiling card
4. fallback and failure card
5. completion receipt card

### 1) Send verdict

Show:

- send label
- send verdict: `in-product-send`, `manual-attachment`, `upload-link-required`, `mobile-export-then-send`, `public-post-minimized-only`, `local-only`, `unknown`
- strongest honest summary
- one next honest action

### 2) Packet membership card

Show:

- what is included now (`debug logs`, `rotated logs`, `profiler`, `crash dump`, `notes only`, `redacted subset`)
- what is explicitly omitted
- whether packet assembly is complete, partial, or blocked
- whether packet membership differs from the last send attempt

### 3) Route and size-ceiling card

Show:

- chosen send route
- route target class
- any route-specific size ceiling or attachment rule
- whether the packet currently fits that ceiling
- whether the route depends on keeping the app open, manual extraction, or later upload

### 4) Fallback and failure card

Show:

- the next honest route if the current send fails (`manual attachment`, `separate upload link`, `local archive for later`, `public minimized post`, `none`)
- whether the fallback widens audience or changes disclosure risk
- partial-send / failed-send evidence, if any
- what the operator must preserve locally before retrying

### 5) Completion receipt card

After send, emit a receipt that preserves:

- packet membership hash / manifest
- selected route
- target class
- size-ceiling verdict
- completion state (`sent`, `queued`, `partial`, `failed`, `unknown`)

## Honest outputs

This page may conclude:

- `private packet fits in-product send lane`
- `packet exceeds attachment ceiling · upload-link fallback required`
- `mobile logs extracted locally; outward send still pending`
- `public minimized summary admissible; raw packet blocked from this lane`

It may not collapse these into one generic `send logs` verdict.

## Rules

### Rule 1 — packet membership and route must remain adjacent

A packet cannot be reviewed honestly if the operator sees included artifacts only after route choice.

### Rule 2 — fallback must be shown before the first failure

Fallback is part of the route contract, not an afterthought discovered after an opaque error.

### Rule 3 — completion must prove more than button click

A send receipt must distinguish `attempted`, `queued`, `completed`, `partial`, and `failed`.

## Acceptance test

This page is good enough when a cautious operator can answer all of the following without leaving it:

- what exact artifacts are in the packet
- by what route they are leaving
- whether the packet fits the lane's size/transport ceiling
- what fallback route is honest if it fails
- what receipt will later prove the send really completed
