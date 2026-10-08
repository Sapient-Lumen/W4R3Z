# Pending effect watch page: staged, live, stale, and proof-expiry interface spec

## Purpose

After a delayed or trigger-bound change is saved, operators need one ordinary page that answers:

> what is still only staged, what is live, what proof is stale, and what next event would honestly upgrade or downgrade the claim?

This page exists so pending changes do not disappear into hidden files, timers, or remembered restart ritual.

## Core decision

Every serious non-immediate or externally-proven change must produce one first-class **Pending effect watch**.

## Fixed page order

1. pending-effect header
2. trigger ledger
3. live-proof timeline
4. residue / non-retroactivity list
5. escalation and supersession rail

### 1) Pending-effect header

Show:

- target / seat / scope
- current watch state (`staged`, `waiting-reread`, `waiting-rescan`, `restart-pending`, `startup-pending`, `live-unverified`, `live-proven`, `proof-stale`, `superseded`, `unknown`)
- strongest safe sentence
- stronger rejected sentence

### 2) Trigger ledger

List each relevant trigger:

- file-change reread
- periodic rescan
- manual rescan
- runtime restart
- next startup
- external observation
- explicit reconcile action

For each trigger show:

- due status
- last occurrence if known
- next opportunity if known
- whether the operator can force it

### 3) Live-proof timeline

Render a timeline with entries such as:

- `value saved`
- `runtime reread observed`
- `restart completed`
- `manual rescan completed`
- `verification witness recorded`
- `proof aged past safe window`
- `newer change superseded prior watch`

### 4) Residue / non-retroactivity list

This list remains visible while the watch is open.
Show:

- objects or claims untouched by the now-live rule
- historical material still requiring separate repair
- earlier receipts that remain valid only for past state
- risks created by assuming full convergence too early

### 5) Escalation and supersession rail

Only show actions such as:

- `Restart runtime now`
- `Run rescan`
- `Verify named examples`
- `Mark proof stale`
- `Supersede with newer change`
- `Open activation receipt`

## Rules

### Rule 1 — pending effect remains visible until resolved or superseded

Saving a change may not silently clear the need for later proof.

### Rule 2 — stale proof is a first-class state

A once-proven effect can age out if the relevant runtime or basis has changed since proof.

### Rule 3 — supersession preserves lineage

A newer edit must not erase the older watch without preserving that it was overtaken before or after proof.

## Acceptance criteria

A later operator can:

- tell whether the change is merely staged or actually live
- tell what trigger or proof is still missing
- tell which old state remains untouched
- tell whether proof has gone stale or been superseded
