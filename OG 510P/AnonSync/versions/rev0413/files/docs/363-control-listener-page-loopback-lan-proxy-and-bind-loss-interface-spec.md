
# Control listener page: loopback, LAN, proxy, and bind-loss interface spec

## Purpose

The archive already had listener-binding and control-trust doctrine.
This document makes the everyday exposure page concrete.

The page exists to answer one ordinary operator question:

> who can reach this control endpoint right now, what exact bind or route makes that true, what happens if the bind disappears, and what stronger or safer exposure state can I move to from here?

## Core decision

Every seat that exposes networked control must own one first-class **Control listener** page.
That page is the semantic home of:

- current listeners
- exposure scope
- bind survivability
- widening and narrowing review
- restart requirements
- listener receipts

## Primary page layout

The page always renders the same top-level regions in the same order:

1. exposure verdict strip
2. current listeners table
3. exposure scope card
4. bind survivability card
5. change review drawer
6. recent listener receipts
7. expert config drawer

### 1) Exposure verdict strip

The strip shows:

- seat name
- strongest current listener verdict
- one current exposure sentence
- next safest action

Allowed verdicts:

- `loopback only`
- `lan reachable`
- `proxy published`
- `remote reachable`
- `listener degraded`
- `no active control listener`

The sentence should say things like `Only this host can currently reach control` or `Control is reachable from the LAN and trust repair is recommended`.

### 2) Current listeners table

Show one row per listener with:

- listener name
- bind target or address class
- port
- trust posture
- expected seat policy
- status (`healthy`, `degraded`, `pending restart`, `blocked`, `inactive`)

The table must separate `configured`, `active now`, and `expected but absent`.

### 3) Exposure scope card

Show:

- who can presently reach the listener
- whether the scope is loopback, subnet, proxy audience, or explicit remote audience
- firewall or gateway dependence
- whether the current surface is safer or broader than the seat's declared default
- last widening or narrowing receipt

This card should answer `what audience did I actually create?`

### 4) Bind survivability card

Show:

- what happens if the bound interface disappears
- whether the engine keeps syncing while control narrows
- whether a restart is required for the current or next state
- fallback control routes if the current bind is lost
- strongest honest degraded state

Possible survivability verdicts:

- `bind loss narrows control only`
- `bind loss leaves alternate listener alive`
- `bind loss will stop control surface`
- `bind loss may stop runtime participation`
- `unknown until restart`

The page must not make interface loss look like daemon identity loss.

### 5) Change review drawer

The drawer contains reviewed actions such as:

- `stay loopback only`
- `widen to lan`
- `publish through proxy`
- `narrow to loopback`
- `change port or handle`
- `retire this listener`

Each action preview shows:

- audience change
- trust consequence
- restart requirement
- whether old deep links or receipts survive
- resulting fallback path if the new bind fails

### 6) Recent listener receipts

Show recent listener/exposure receipts with:

- old exposure class
- new exposure class
- actor
- restart required or not
- surviving fallback route
- linked detail receipt

### 7) Expert config drawer

Hide raw bind strings, proxy/backend config, firewall hints, and route diagnostics behind an expert drawer.
Those details matter, but they should not replace the typed page answer.

## Narrow-width behavior

In narrow width the page may compress the listener table, but it may not hide:

- current audience
- whether scope widened or narrowed
- bind-loss consequence
- next safest exposure action

## Acceptance criteria

This spec is satisfied when:

- an operator can tell from one page who can reach control right now
- loopback, LAN, proxied, and remote exposure are visibly different states
- bind loss and engine continuity are not silently conflated
- widening or narrowing exposure always leaves a listener receipt and consequence preview
