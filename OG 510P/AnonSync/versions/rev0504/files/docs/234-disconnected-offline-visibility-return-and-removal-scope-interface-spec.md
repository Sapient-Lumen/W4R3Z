# Disconnected/offline visibility, return semantics, and removal-scope interface spec

## Purpose

The archive already had device-retirement and departure semantics.
What it still lacked was one stricter contract for a cluster of meanings that current sync tools often flatten together:

> is this thing offline, hidden, disconnected, pending, removable only here, removable everywhere in my constellation, or still reachable by parties outside that constellation?

Current Resilio docs make this seam concrete.
Their current folder docs still say disconnected folders have no local path yet remain visible for future action, and removing a disconnected folder removes it from all linked devices.
Their current remove/disconnect docs still say reconnect may propose a different path and create a new directory, and that removal from linked devices may still leave the folder available on other remote devices not linked to the same identity.
Their current offline-device docs still say `Hide this device` does not unlink the device and it will reappear if it comes back online.

That means list visibility still does not equal control scope.

## Core decision

AnonSync must separate **row visibility**, **local participation**, **constellation membership**, and **external reachability**.

Every row that represents a seat or subject in a degraded or absent state must declare:

- whether it is merely hidden versus actually detached
- whether its removal is local, constellation-wide, or broader
- whether it can return automatically
- whether bytes or authority still exist elsewhere

## Why this matters

Current Resilio behavior still spreads the answer across different pages:

- disconnected subjects stay as action rows without a local path
- removing a disconnected subject propagates across linked devices
- other non-linked devices may still retain the subject
- hidden offline devices are cosmetic removals and can later reappear
- reconnect can silently drift path continuity unless the operator repairs it manually

AnonSync should therefore hold one stronger rule:

> every absent-looking row must carry an explicit return contract and an explicit removal scope.

## Fixed review order

Every disconnect, hide, return, or remove action should render the same sections in the same order:

1. **Current row meaning**
2. **Return semantics**
3. **Removal scope**
4. **Residual presence elsewhere**
5. **Departure / return receipt**

### 1) Current row meaning

Classify the row as exactly one of:

- `pending`
- `inbox-only`
- `disconnected-local`
- `hidden-offline`
- `retired`
- `revoked`
- `externally-present`
- `other reviewed state`

Do not reuse `offline` as a catch-all.

### 2) Return semantics

Show:

- whether the row can auto-return
- what event triggers return (`peer online`, `re-issue`, `manual reconnect`, `manual relink`, `never`)
- whether a path or placement choice will be required again
- whether return may create a new directory unless continuity is explicitly repaired

### 3) Removal scope

Show one explicit scope choice:

- `hide only on this seat`
- `disconnect only on this seat`
- `remove from this constellation`
- `revoke externally and locally`
- `local bytes only`
- `reviewed custom scope`

### 4) Residual presence elsewhere

Show:

- linked seats still carrying the subject
- external non-linked seats still carrying the subject
- whether placeholders, bytes, or only receipts remain locally
- whether authority to reconnect still exists

The operator must be able to answer:

> after I do this, who still has the thing, who can bring it back, and what exact row should I expect later?

### 5) Departure / return receipt

The receipt must preserve:

- state before and after
- removal scope chosen
- residual-presence findings
- return trigger
- path continuity outcome if later reconnected

## Main surface

Every subject and seat list should support columns or chips for:

- state class
- return posture
- removal scope
- external residual presence
- last seen / last returned

A hidden row must be discoverable through a dedicated `Hidden` or `Absent` view, not simply vanished.

## Acceptance criteria

This spec is satisfied when:

- hidden/offline/disconnected/revoked are never conflated
- removal scope is always legible before apply
- automatic return is always described as a contract, not a surprise
- operators can distinguish local cleanup from constellation-wide departure and from external residual reachability
