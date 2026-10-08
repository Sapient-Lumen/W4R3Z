# Transfer eligibility contract sheet page: policy gates, context gates, lane truth, and timing modifiers interface spec

## Purpose

Before an operator trusts a pause, waits for a wake-up, narrows a mobile/network rule, or assumes nothing more can move, they need one ordinary page that answers:

> what lanes are eligible right now, what gates are blocking others, what still mutates despite the visible badge, and what is the strongest honest sentence the product can still say?

This page exists so `paused`, `offline`, `sleeping`, `Wi‑Fi only`, `battery blocked`, `delay-held`, and `priority-deferred` do not remain support-only distinctions.

## Core decision

Every serious subject/runtime pair must open one first-class **Transfer eligibility contract sheet**.

The sheet owns:

- current eligibility verdict
- policy gates
- context gates
- lane-by-lane truth
- timing modifiers
- wake / resume witness
- strongest safe sentence
- stronger rejected sentence

## Fixed page order

1. eligibility claim header
2. lane truth card
3. policy and context gate card
4. timing and queue modifier card
5. wake / retry card
6. claim ceiling and next-safe action rail

### 1) Eligibility claim header

Show at minimum:

- subject / seat / node name
- overall verdict (`fully-eligible`, `transfer-blocked-detecting`, `paused-with-mutations`, `sleeping`, `context-blocked`, `battery-stopped`, `delay-held`, `priority-deferred`, `runtime-stopped`, `unknown`)
- strongest safe sentence
- stronger rejected sentence
- evidence freshness

Example safe sentence:

- `Payload transfer is blocked by current policy and context gates, but indexing remains active and the product cannot honestly claim a fully quiet subject.`

### 2) Lane truth card

Render rows for at least these lanes:

- payload upload
- payload download
- deletion publication
- zero-byte / structural marker publication
- local change detection
- indexing / queue growth
- peer visibility / online appearance
- scheduled wake / recheck

Each row shows:

- current state (`eligible`, `blocked`, `deferred`, `active`, `unknown`)
- basis
- freshness
- operational consequence

### 3) Policy and context gate card

Separate **policy gates** from **context gates**.

Policy gate examples:

- `no-cellular`
- `share-paused`
- `scheduled-zero-window`
- `manual-throttle`
- `delay-rule`
- `queue-priority-policy`

Context gate examples:

- `currently-on-cellular`
- `below-battery-threshold`
- `core-asleep`
- `background-priority-lowered`
- `queue-full`
- `unknown-network-state`

Each gate row shows:

- source plane
- current effect
- whether the operator can change it here
- whether it blocks a stronger claim

### 4) Timing and queue modifier card

Show modifiers that are weaker than `blocked` but stronger than `moving freely`:

- file-class publication delay
- queue priority mode
- queue rank if known
- whether lower-priority work is suspended
- whether the modifier is global, share-scoped, or file-scoped

### 5) Wake / retry card

Show:

- next wake time or interval if known
- event that will restore eligibility (`join-approved-network`, `battery-above-threshold`, `charge-connected`, `scheduler-window`, `manual-resume`, `runtime-revive`)
- whether retry is automatic or manual
- whether a stronger claim is waiting on that event

### 6) Claim ceiling and next-safe action rail

Only show actions that preserve meaning, such as:

- `Open mobility and power budget review`
- `Open eligibility proof`
- `Resume eligible lanes`
- `Change network / battery policy`
- `Emit eligibility boundary receipt`

## Rules

### Rule 1 — one badge can never compress all lane truth

The operator must never have to infer from `Paused` or `Stopped` whether deletes, rescans, delay rules, or queue precedence still apply.

### Rule 2 — modifiers are not gates

Delay and priority may explain slow or absent movement without meaning the runtime is stopped.

### Rule 3 — strongest safe sentence comes after lane truth, not before it

The surface earns the sentence by showing the lanes and gates first.
