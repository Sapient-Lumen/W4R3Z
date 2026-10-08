
# Browser trust recovery page: warning cause, temporary exception, and durable fix interface spec

## Purpose

The archive already had control-trust doctrine.
This document makes the browser-warning moment concrete as one page.

The page exists to answer one ordinary operator question:

> why is the browser distrusting this endpoint, what does a one-time exception actually do, what durable fix is available, and what residue or return path remains afterward?

## Core decision

Every browser-mediated control flow that encounters distrust must route through one first-class **Browser trust recovery** page.
That page is the semantic home of:

- current warning cause
- endpoint proof
- temporary exception meaning
- durable fix ladder
- residue such as cached distrust or old pins
- trust-repair receipts

Browser chrome must never be the primary explanation surface.

## Primary page layout

The page always renders the same top-level regions in the same order:

1. warning verdict strip
2. endpoint proof card
3. warning-cause card
4. temporary path card
5. durable fix ladder
6. residue and return-path card
7. recent trust-repair receipts

### 1) Warning verdict strip

The strip shows:

- seat name
- endpoint being accessed
- one explicit trust-recovery verdict
- strongest safe next action

Allowed verdicts:

- `local bootstrap certificate`
- `hostname mismatch`
- `expired or rotated certificate`
- `cached browser distrust residue`
- `plaintext local-only endpoint`
- `unexpected remote endpoint`
- `unknown distrust cause`

### 2) Endpoint proof card

Show:

- endpoint class
- listener identity / fingerprint handle
- who established current trust state
- whether this browser profile has seen this endpoint before
- current trust grade and expiry when applicable

This card should answer `am I at least talking to the endpoint I intended?`

### 3) Warning-cause card

Translate the browser/OS warning into product language:

- why the warning appeared
- whether the cause is expected for this seat
- whether the risk is only local bootstrap, broader remote exposure, or possible impostor state
- what facts are known versus inferred

The page must not ask the operator to decode generic browser prose unaided.

### 4) Temporary path card

If a temporary bypass is admissible, show exactly:

- what the one-time exception does
- whether it is browser-profile specific
- whether it survives reload or session end
- what it does **not** fix
- what stronger state is still recommended next

If no temporary path is admissible, say so plainly.

### 5) Durable fix ladder

List the durable next states in strength order.
Each row shows:

- target trust grade
- what technical change is required
- whether restart is needed
- whether browser residue must also be cleared
- whether old deep links or sessions survive
- action button

Typical actions include:

- `pin this local endpoint`
- `install trusted certificate`
- `rotate certificate and retire old trust`
- `return to loopback-only`
- `open control on a safer local path`

### 6) Residue and return-path card

Show any remaining residue such as:

- cached HSTS / distrust state
- stale pins or remembered trust
- old certificate still seen by another browser profile
- session continuity risk after trust change
- fallback local return path if the browser remains blocked

This card prevents the operator from thinking the certificate and the browser memory are the same thing.

### 7) Recent trust-repair receipts

Show recent trust-repair receipts with:

- warning cause
- chosen temporary or durable path
- endpoint
- actor
- resulting trust grade
- remaining residue if any

## Narrow-width behavior

In narrow width the page may stack cards, but it may not hide:

- warning cause
- temporary-vs-durable distinction
- strongest durable fix
- remaining residue

## Acceptance criteria

This spec is satisfied when:

- browser distrust is explained in product language rather than chrome folklore
- one-time exception and durable fix are never conflated
- browser residue such as cached distrust remains visible after endpoint changes
- any chosen path leaves a trust-repair receipt
