# Local eviction page: placeholder reversion, detach scope, and last-full-copy floor interface spec

## Purpose

The archive already has strong residue, retention, and continuity doctrine.
This document makes the ordinary page concrete.

The page exists to answer one ordinary operator question:

> if I remove this from this device, revert it to a placeholder, or disconnect this folder here, what leaves this seat only, what stays elsewhere, and am I about to strand the last usable full copy?

## Core decision

Every serious selective-materialization system must own one first-class **Local eviction** page.
That page is the semantic home of:

- eviction target and scope
- current local/full-copy distribution
- resulting local state (`placeholder`, `detached but preserved`, `absent`)
- last-full-copy floor
- continuity and reacquireability verdict
- strongest next-safe action

The product must not let `Remove from this device`, `Disconnect`, or local delete gestures stand in for this page.

## Primary page layout

The page always renders the same top-level regions in the same order:

1. target strip
2. current distribution card
3. local-only effect card
4. full-copy floor card
5. resulting local state card
6. reacquire and continuity card
7. strongest-next-action card
8. recent eviction receipts
9. expert details drawer

### 1) Target strip

Show:

- target (`file`, `subtree`, `entire subject`, or `disconnect subject on this seat`)
- acting seat
- current strongest risk phrase
- strongest next-safe action

The strip should answer `what am I about to stop holding here?`

### 2) Current distribution card

Show:

- whether this seat currently has a full copy, placeholders only, or a disconnected listing
- how many other seats are known to hold a full copy now
- whether any retained-history copy exists locally
- whether any dependent policy assumes continued local materialization here

This card should answer `how much real material exists before I evict?`

### 3) Local-only effect card

Show one explicit local-effect verdict:

- `revert to placeholder only`
- `remove placeholder names and detach subject on this seat`
- `remove local bytes but preserve retained history`
- `insufficient evidence to promise harmless local-only eviction`

Also show the strongest sentence explaining why.

### 4) Full-copy floor card

Show:

- whether at least one other trusted full copy remains
- whether this action would leave zero known full copies and only placeholders
- whether the remaining full copies are route-reachable enough for future reacquire
- whether retained history is a true recovery floor or only a weak last resort

This card should answer `am I about to strand the only real copy?`

### 5) Resulting local state card

Show:

- resulting local subject state on this seat
- whether file names remain visible as placeholders
- whether folder presence remains as detached inventory only
- whether any local bytes, history, or receipts remain behind

This card should answer `what will I still see here after eviction?`

### 6) Reacquire and continuity card

Show:

- whether reacquire will be one click, one reviewed reconnect, or impossible without another full-copy witness
- whether future arrivals continue to be visible after eviction
- whether disconnect changes future default posture for this subject or only current local presence
- whether path continuity is preserved or a later reconnect may create a new local bind

This card should answer `how hard is it to get this back honestly later?`

### 7) Strongest-next-action card

Show the strongest honest next action, for example:

1. `Evict local bytes and keep placeholders`
2. `Disconnect subject on this seat`
3. `Keep one local full copy because no remote witness exists`
4. `Open delete-consequence review instead`
5. `Open restore review because history is the only remaining floor`
6. `Wait until another full-copy witness appears`

This card should answer `what is the safest next move?`

### 8) Recent eviction receipts

Show recent receipts with:

- target
- resulting local state
- full-copy floor verdict
- remote witness count
- reacquire verdict
- action taken

### 9) Expert details drawer

Hide per-path placeholder maps, route candidates, hash witness detail, and policy derivation traces behind an expert drawer.
They matter, but they are not the semantic center.

## Compact row contract

A trustworthy compact row should preserve the following order:

1. target phrase
2. current-copy phrase
3. resulting-local-state phrase
4. full-copy-floor phrase
5. strongest next action

Example:

```text
Invoices/2025 subtree · full local copy here · evicting leaves placeholders and 2 remote full copies · reacquire safe later · Evict local bytes
```

## Mandatory fields

- `target_ref`
- `target_scope_verdict`
- `acting_seat_ref`
- `current_local_state_verdict`
- `remote_full_copy_witness_refs[]`
- `retained_history_presence_verdict`
- `local_only_effect_verdict`
- `resulting_local_state_verdict`
- `last_full_copy_floor_verdict`
- `reacquireability_verdict`
- `future_visibility_after_eviction_verdict`
- `path_continuity_verdict`
- `strongest_next_action`

## Review guarantees

This page must let the operator:

- tell whether the action is truly local-only
- tell whether placeholders, detached inventory, or nothing will remain visible here
- tell whether another trustworthy full copy survives elsewhere
- move directly into safe eviction, disconnect, wait, or deeper delete / restore review without reopening the world
