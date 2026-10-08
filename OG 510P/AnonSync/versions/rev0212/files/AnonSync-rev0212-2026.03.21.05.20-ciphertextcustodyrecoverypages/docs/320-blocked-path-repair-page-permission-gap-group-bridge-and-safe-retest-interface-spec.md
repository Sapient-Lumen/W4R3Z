# Blocked-path repair page: permission gap, group bridge, and safe retest interface spec

## Purpose

This page answers one ordinary question:

> this path is blocked for the current execution principal; what exact repair rung is safest, and what retest will prove the path is healthy again without causing a larger continuity mistake?

The page exists because blocked-path repair is rarely one move.
It may involve grant correction, group bridging, provider regrant, principal switch, mount correction, or full rebind.

## Core decision

Every path blocked by authority failure must open one first-class **Blocked-path repair** page.
That page owns:

- blocked path identity
- narrowest permission gap
- ordered repair rungs
- cross-world warning if authority repair escalates into principal switching
- post-repair retest proof
- the final repair receipt

The workbench must not force the operator to jump from a warning row into scattered host-specific folklore.

## Primary layout

The page always renders the same regions in the same order:

1. blocked-path strip
2. blocker diagnosis card
3. repair ladder card
4. retest card
5. escalation boundary card
6. repair receipts

### 1) Blocked-path strip

Show:

- subject label
- path or provider handle
- current execution principal
- current verdict: `grant-missing`, `grant-partial`, `mount-weak`, `provider-stale`, `world-switch-required`, `uncertain`
- one next honest action

### 2) Blocker diagnosis card

This card publishes:

- exact blocked operation
- narrowest known blocker location
- strongest evidence for the blocker
- whether the failure is persistent or intermittent
- whether the problem is grant, mount, principal, or mixed

### 3) Repair ladder card

This card publishes an ordered list of rungs from least world-disruptive to most:

- recheck / retest only
- repair path grant in place
- bridge group / ACL / NAS internal-user grant in place
- refresh provider token or remount
- escalate runtime principal within same world if possible
- successor-world switch with rebind work

Each rung must state:

- expected authority gain
- continuity risk
- reversibility
- what stronger rung it makes unnecessary if successful

### 4) Retest card

This card publishes:

- exact local operations that will count as success
- whether the retest proves directory write, file replace, rename, delete, or only a subset
- the evidence window after repair
- whether remote progress may still lag even after local authority is restored

### 5) Escalation boundary card

This card publishes:

- whether the next rung crosses from grant repair into world switch
- what checkpoint is required before that escalation
- what inventory or identity custody may change if escalated

### 6) Repair receipts

Receipts show:

- diagnosis updates
- chosen rung
- retest outcomes
- escalations
- final verdict
- the actor and time

## Non-negotiable rules

### Rule 1 — the ladder must prefer authority repair over world replacement when possible

If in-place grant repair can solve the problem, the page must not jump straight to a stronger principal or fresh world.

### Rule 2 — retest must be operation-specific

A successful read test does not prove replace or delete.
The retest card must publish exactly which operations passed.

### Rule 3 — successor-world escalation must be labeled as such

If the only remaining fix is a principal switch or storage-root change that creates a new local world, the page must say so plainly before apply.

## Honest outputs

The page may conclude:

- `Missing group write on directory root; in-place grant repair is sufficient and reversible.`
- `NAS internal-user grant absent; no principal switch required.`
- `Provider token stale; refresh should restore create/replace without changing world.`
- `Only Local System has the needed reach, but that escalation creates a successor world and requires rebind work.`

It may not collapse those outcomes into one generic `fix permissions` button.
