# Background delivery page: suspend gates, freshness floor, and catch-up risk interface spec

## Purpose

This page owns the answer to:

> while I am not staring at this surface, will this seat keep detecting, sending, and receiving changes; what can suspend that behavior; and what catch-up risk appears afterward?

The page exists because `online` is not an honest enough answer.
Background delivery depends on platform, runtime, battery, network, and byte posture.

## Core decision

Every seat must expose one first-class **Background delivery** page.
That page owns:

- platform background eligibility
- current suspend gates
- freshness floor while unattended
- wake or catch-up interval
- mutation-risk notes after offline / suspended periods

## Primary layout

The page renders the same regions:

1. background strip
2. eligibility card
3. suspend-gates stack
4. freshness and catch-up card
5. receipts and actions

### 1) Background strip

Show:

- current seat/surface
- verdict: `continuous`, `conditional`, `foreground-only`, `stopped`
- one next honest action

### 2) Eligibility card

Show:

- whether the platform/runtime can deliver in background at all
- whether hidden window / tray / headless web still counts as active runtime
- whether foreground-only constraints apply
- whether current byte posture or missing bytes weaken background usefulness

### 3) Suspend-gates stack

Show the currently winning gates in precedence order, for example:

- app fully closed
- battery saver
- auto-sleep
- forbidden network / Wi-Fi-only miss
- OS task killer or memory pressure
- host asleep or storage unavailable
- permission / connectivity block

Each gate shows:

- whether it merely delays or fully blocks
- whether remote changes are still accumulating elsewhere
- exact condition to clear the gate

### 4) Freshness and catch-up card

Show:

- expected unattended freshness floor
- next wake / poll / resume expectation if not continuous
- whether a restart or foreground return triggers re-index or catch-up scan
- whether offline local edits introduce stale-overwrite or conflict risk on resume

### 5) Receipts and actions

Receipts show suspension, resume, and catch-up events.
Actions may include:

- `Permit stronger background operation`
- `Change battery / sleep rule`
- `Allow network`
- `Open foreground catch-up now`
- `Reveal resume risk explanation`

## Rules

### Rule 1 — background truth must be platform-specific and current

The page must distinguish `desktop hidden but active`, `headless web runtime`, `android conditional background`, and `foreground-only` states.

### Rule 2 — suspend reasons must be named, not guessed

The page must publish the winning current gate instead of leaving the operator to guess whether nothing is happening because of battery, network, permissions, or platform law.

### Rule 3 — catch-up risk must stay adjacent to resume

If resume can re-index, overwrite stale edits, or otherwise widen risk, the page must state that before the operator trusts freshness.

## Honest outputs

The page may conclude:

- `continuous background delivery`
- `conditional background delivery`
- `foreground-only delivery`
- `suspended by battery or network gate`
- `resume carries stale-edit risk`

It may not flatten all of those into one generic `offline` or `paused` badge.
