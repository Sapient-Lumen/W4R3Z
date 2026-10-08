# Peer memory override page — retention, route residue, and clearance interface spec

## Purpose

The archive already had discovery-basis and exposure-widening pages.
What it still lacked was one ordinary page for the simpler question:

> how long does this seat remember peers and route facts, what stale residue is still shaping claims, and what exact clearance action is required to narrow or forget it?

Current official Resilio docs make this seam concrete.
They still keep peer-retention truth, tracker/relay refresh cadence, and LAN-only residue-clearing behavior split across advanced preferences, folder preferences, and special-case instructions.
That is useful truth.
It should not remain folklore.

## Core decision

AnonSync must expose one first-class **Peer memory override** page whenever hidden settings can materially change peer retention, stale-route persistence, discovery refresh cadence, or the clearance ritual required after narrowing exposure.

The page exists to answer five things in one place:

1. what memory and refresh posture is currently active
2. which peer and route facts are still retained
3. how long they live and how often they refresh
4. what explicit clearance is needed to forget wider facts
5. what next action is least misleading

## Fixed page order

1. **Current memory and cadence verdict**
2. **Retained-facts register**
3. **Expiry and refresh timers**
4. **Clearance review**
5. **Safe next actions**

### 1) Current memory and cadence verdict

Show:

- `peer_memory_override_page_id`
- seat and optional subject in scope
- current `memory_verdict` (`default-retention`, `extended-retention`, `short-retention`, `immediate-clearance-mode`, `stale-route-residue`, `surface-claim-ahead-of-clearance`, `unknown`)
- strongest honest summary
- last evaluated time

The operator must be able to answer:

> is this seat still remembering wider peer or route facts than the visible surface currently implies?

### 2) Retained-facts register

Show retained families such as:

- peer roster entries
- remembered public endpoints
- discovery catalog state
- tracker / relay metadata snapshots
- known-host pins or declared discovery aids

Each row must distinguish `currently authoritative`, `cached`, `stale-but-still-effective`, and `awaiting-clearance`.

### 3) Expiry and refresh timers

Show:

- peer-expiration timer
- discovery catalog refresh timer
- config-save timer if it gates durable change visibility
- restart requirement if needed
- whether expiry alone is enough or whether explicit clearance is faster / required

This section must answer:

> how long until this wider memory stops shaping behavior if I do nothing?

### 4) Clearance review

Show the least-misleading clearance plan with:

- required steps in order
- facts that will be forgotten
- facts that may remain until peers reconnect differently
- why a narrower visible toggle alone is not yet sufficient
- whether the action is reversible or only re-learnable later

### 5) Safe next actions

Actions may include:

- `Expire peer memory now`
- `Restart and re-evaluate`
- `Confirm narrower discovery posture`
- `Accept residue until expiry`
- `Open reachability basis`
- `Export clearance receipt`

Each action must preview whether it changes retained memory, live connectivity, or both.

## Public object

### Peer memory override page

Fields:

- `peer_memory_override_page_id`
- `seat_ref`
- `subject_ref` nullable
- `memory_verdict`
- `retained_fact_rows[]`
- `timer_rows[]`
- `clearance_plan[]`
- `safe_next_actions[]`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. retained fact family
2. current state
3. expiry / refresh timer
4. strongest residue consequence
5. next safest action

Example:

```text
remembered public endpoint     stale-but-still-effective     peer retention 7d / refresh 3600s     LAN-only claim not yet fully true     Expire peer memory now
```

## Non-goals

This page does **not** replace route proof or full connectivity repair.
It proves only **what peer and route memory is still retained, how long it lasts, and what clearance ritual is honestly required to forget it**.
