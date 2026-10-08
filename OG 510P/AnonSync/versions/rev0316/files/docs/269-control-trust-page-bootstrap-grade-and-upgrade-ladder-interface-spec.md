# Control trust page: bootstrap grade, endpoint proof, and upgrade ladder interface spec

## Purpose

`237` established the semantic contract for control-channel trust.
This document makes it concrete as one page.

The page exists to answer one ordinary operator question:

> what browser-controlled endpoint am I talking to right now, why is the trust posture what it is, and what stronger safer state can I move to from here?

## Core decision

Every seat that exposes browser/local-web control must own one first-class **Control trust** page.
That page is the semantic home of:

- endpoint identity
- current trust grade
- browser-warning cause
- allowed upgrade or exception paths
- the last trust receipt

The browser chrome must never be the primary explanation surface.

## Primary page layout

The page always renders the same top-level regions in the same order:

1. page header and current verdict
2. endpoint card
3. trust-grade card
4. why-this-browser-warns card
5. upgrade ladder
6. recent trust receipts
7. destructive / degraded actions drawer

### 1) Page header and current verdict

The header shows:

- seat name
- host name
- current endpoint class
- one current verdict chip
- one next-safest-action button

Allowed verdicts:

- `trusted certificate`
- `pinned local bootstrap`
- `temporary exception`
- `plaintext local only`
- `degraded / unverified`

The next-safest-action button must name a stronger state, not merely `settings`.

### 2) Endpoint card

Show:

- listener address and port
- whether endpoint is loopback, LAN, proxied, or remote
- whether listener is expected for this seat profile
- current exposure scope
- last listener mutation receipt

If the seat is loopback-only, say so plainly.
If the endpoint is LAN- or proxy-reachable, say so plainly.

### 3) Trust-grade card

Show:

- current trust grade
- why this grade was chosen
- who or what established it
- when it expires or rotates
- whether the current browser profile is already pinned

This card should answer the question `is this good enough for what I am doing right now?`

### 4) Why-this-browser-warns card

This card must translate browser/OS distrust into product language.
Possible causes include:

- self-signed bootstrap certificate
- hostname mismatch
- remote/proxied endpoint without trusted certificate
- expired or replaced certificate
- no TLS because seat is intentionally loopback-only plaintext

The page must not ask the operator to infer semantics from generic browser wording alone.

### 5) Upgrade ladder

The ladder lists allowed next states in strength order.
Each row shows:

- target trust grade
- what changes technically
- whether exposure widens
- whether restart is needed
- whether old receipts stay valid
- action button

Typical actions:

- `pin this local endpoint`
- `install certificate`
- `rotate certificate`
- `switch to loopback-only`
- `allow one temporary exception`
- `abort and inspect`

### 6) Recent trust receipts

Show the last few trust mutations as a compact ledger:

- old grade
- new grade
- actor
- seat
- certificate fingerprint or pin id
- duration / expiry
- linked detail receipt

### 7) Destructive / degraded actions drawer

Place weaker choices behind a clearly named drawer such as `Temporary or degraded paths`.
That drawer may contain:

- one-time exception
- temporary plaintext local-only fallback
- revoke current pin

The page must state the risk and the exact downgrade created.

## Page behavior in narrow width

In narrow width the page may collapse cards into stacked sections, but it may not hide:

- current trust grade
- why the browser distrust exists
- next safer upgrade path
- recent trust receipt

## Jump links from elsewhere

The page must be reachable from:

- browser warning interception
- seat settings
- listener configuration
- login/reset flows
- bringup pages when control reachability exists but trust is degraded

## Acceptance criteria

This spec is satisfied when:

- an operator can answer endpoint class, trust grade, warning cause, and next safer action from one page
- temporary exception and durable upgrade are never conflated
- the product leaves its own receipt for trust mutations
- a degraded state always names the next stronger reachable state
