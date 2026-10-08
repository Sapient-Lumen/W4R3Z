# Identity-graph adoption contract sheet page: certificate graph direction, graph replacement, and entitlement coupling interface spec

## Purpose

Before an operator links a device into an identity, changes identity, accepts graph-wide auto-arrival, or begins compromise containment, they need one ordinary page that answers:

> what graph is this seat about to join, which certificate will survive, what rights and future arrivals come with membership, and what stronger containment or ownership sentence is still blocked?

This page exists so `Link device` does not remain an over-compressed convenience button.

## Core decision

Every serious identity-graph action must open one first-class **Identity-graph adoption contract sheet**.

The sheet owns:

- current certificate / fingerprint class
- proposed adoption direction
- graph replacement class
- linked-arrival default mode
- default authority class
- entitlement / license coupling class
- containment class
- strongest safe sentence
- stronger rejected sentence

## Fixed page order

1. identity claim header
2. direction and survivor card
3. arrival and rights card
4. entitlement and containment card
5. proof card
6. claim ceiling and next-safe action rail

### 1) Identity claim header

Show at minimum:

- local seat / remote seat / current identity names
- current certificate verdict (`independent`, `already-linked`, `replacement pending`, `unknown`)
- adoption direction verdict (`local adopts remote`, `remote adopts local`, `already-same-graph`, `unknown`)
- graph replacement verdict (`no replacement`, `shares will be imported`, `advanced-subject app removal expected`, `unknown`)
- strongest safe sentence
- stronger rejected sentence
- evidence freshness

Example safe sentence:

- `Linking will place this seat into the remote identity graph and may replace this seat's current certificate and visible share roster.`

### 2) Direction and survivor card

Render rows for:

- which certificate survives
- which fingerprint becomes authoritative here
- whether current local shares remain, disappear from app, or are unknown
- storage survivor class (`app-roster replacement only`, `filesystem bytes survive`, `platform exception risk`, `unknown`)
- version-compatibility risk (`same major`, `mixed-major risk`, `unknown`)

### 3) Arrival and rights card

Separate these truths explicitly:

- future folder auto-arrival yes/no/unknown
- default arrival mode (`disconnected`, `selective`, `synced`, `unknown`)
- default authority class (`owner-lane`, `rw-lane`, `manual-share exception required`, `unknown`)
- RO exception path (`not available in linked lane`, `manual standard-key workaround`, `unknown`)

### 4) Entitlement and containment card

Show:

- license coupling (`inherits linked-owner entitlement`, `independent entitlement`, `ownership-steal risk`, `unknown`)
- hide-offline vs unlink distinction
- local-only unlink capability
- compromise response class (`hide only`, `unlink local`, `identity reset`, `unknown`)

### 5) Proof card

Show the current proof rung:

- `documented behavior only`
- `certificates/fingerprints compared`
- `direction explicitly chosen`
- `license owner class known`
- `containment/reset path rehearsed`

### 6) Claim ceiling and next-safe action rail

Only show actions that preserve meaning, such as:

- `Open certificate takeover review`
- `Open linked-graph default arrival and rights page`
- `Open identity containment reset proof`
- `Emit identity lineage receipt`

## Rules

### Rule 1 — linking may not be framed as neutral pairing

The page must publish who adopts whom.

### Rule 2 — graph membership and folder authority must remain separate

Being in the same identity graph is different from the exact default mode and authority posture with which subjects arrive.

### Rule 3 — containment language must stay honest

`hide`, `unlink`, and `identity reset` must never collapse into one reassuring verb.

### Rule 4 — the page must refuse stronger language it cannot prove

Blocked examples:

- `this is just a harmless name sync`
- `nothing on this device will be displaced`
- `we can undo compromise by unlinking one seat later`
