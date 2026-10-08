# Diagnostic lane contract sheet page: capture family, support lane, and residue ceiling interface spec

## Purpose

Before an operator enables debug logging, starts profiler capture, prepares a crash-artifact watch, or sends evidence outward, they need one ordinary page that answers:

> what exact diagnostic lane am I entering, what support or disclosure lane is actually available, what local evidence will this create, and what stronger claim is still blocked?

This page exists so `Enable debug logging` never remains a magical toggle.

## Core decision

Every serious diagnostic-affecting action must open one first-class **Diagnostic lane contract sheet**.

The sheet owns:

- capture family
- activation route
- support / disclosure lane
- restart and hold-time boundary
- local artifact classes
- rotation / TTL / cleanup boundary
- strongest safe sentence
- stronger rejected sentence

## Fixed page order

1. diagnostic claim header
2. capture-family card
3. support-lane card
4. sufficiency and residue card
5. disclosure / send card
6. claim ceiling and next-safe action rail

### 1) Diagnostic claim header

Show at minimum:

- requested diagnostic lane (`anonymous-metrics`, `debug-logs`, `profiler`, `crash-watch`, `mixed`, `unknown`)
- current active lane if one already exists
- lane delta (`new lane`, `lane widen`, `hold-time extension`, `send only`, `cleanup only`, `unknown`)
- strongest safe sentence
- stronger rejected sentence
- evidence freshness

Example safe sentence:

- `This action opens a local debug-log capture lane with restart and hold-time obligations; it does not by itself prove staffed vendor support is available.`

### 2) Capture-family card

Render rows for:

- capture primitive (`anonymous statistics`, `debug log`, `profiler trace`, `crash artifact`, `mixed`, `unknown`)
- activation route (`settings toggle`, `power-user setting`, `debug file`, `automatic crash watch`, `manual artifact collection`, `unknown`)
- restart boundary (`not required`, `required`, `already satisfied`, `unknown`)
- hold-time basis (`none`, `time-window`, `reproduce-then-wait`, `crash-event`, `unknown`)

### 3) Support-lane card

Separate these truths explicitly:

- support lane (`staffed vendor support`, `self-serve forum/help-center`, `billing/licensing web form`, `private operator only`, `unknown`)
- entitlement basis (`business`, `v3 self-serve`, `mobile local export only`, `unknown`)
- send route class (`automatic feedback`, `manual attachment`, `out-of-band upload`, `manual local extraction`, `unknown`)

### 4) Sufficiency and residue card

Show:

- sufficiency class (`too-early`, `awaiting-restart`, `collecting`, `ready-for-review`, `stale`, `unknown`)
- local artifact set (`sync.log`, `sync.log.old`, zipped rotations, `profiler.dat`, crash dump, hidden mobile logs, `unknown`)
- residue class (`temporary but retained`, `size-rotated`, `ttl-bound`, `manual cleanup needed`, `unknown`)
- cleanup ceiling (`disable only`, `cleanup available`, `manual deletion required`, `unknown`)

### 5) Disclosure / send card

Show:

- outbound audience class (`vendor`, `community`, `teammate`, `private archive`, `none yet`, `unknown`)
- redaction posture (`not reviewed`, `reviewed-minimized`, `raw local only`, `unknown`)
- send-readiness class (`blocked`, `not yet sufficient`, `ready`, `sent`, `unknown`)

### 6) Claim ceiling and next-safe action rail

Only show actions that preserve meaning, such as:

- `Open debug capture review`
- `Open crash and profiler custody page`
- `Open external support lane proof`
- `Emit diagnostic lane lineage receipt`

## Rules

### Rule 1 — capture family may not be reduced to one diagnostics noun

The page must publish whether this is metrics, logs, profiler, crash capture, or some reviewed mixture.

### Rule 2 — local residue must stay visible

The product must show which artifacts may remain on disk even after send or stop.

### Rule 3 — support lane and send lane must stay separate

A staffed vendor lane must never be implied by the mere existence of a send button.

### Rule 4 — sufficiency language must stay honest

Blocked examples:

- `Diagnostics are on, you can send now`
- `Support package ready`
- `Capture complete`

unless restart/hold-time and artifact readiness are actually proven.
