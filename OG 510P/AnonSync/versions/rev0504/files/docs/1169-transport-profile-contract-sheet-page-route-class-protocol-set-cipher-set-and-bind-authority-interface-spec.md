# Transport profile contract sheet page: route class, protocol set, cipher set, and bind authority interface spec

## Purpose

Before an operator narrows route options, pins an interface, hardens LAN transport, or forces protocol / cipher subsets, they need one ordinary page that answers:

> what transport classes are still in play here, what do these peers actually share in common, and which stronger sentence is still blocked?

This page exists so `advanced network settings` never remain a scattered table.

## Core decision

Every serious transport-affecting action must open one first-class **Transport profile contract sheet**.

The sheet owns:

- effective route class set
- configured protocol set
- common protocol overlap
- configured cipher set
- common cipher overlap
- bind posture
- fallback posture
- strongest safe sentence
- stronger rejected sentence

## Fixed page order

1. transport claim header
2. route class card
3. protocol overlap card
4. cipher overlap card
5. bind and fallback card
6. proof ceiling and next-safe action rail

### 1) Transport claim header

Show at minimum:

- target scope (`seat`, `subject`, `pair`, `cohort`, `unknown`)
- requested transport posture (`direct-preferred`, `relay-allowed`, `lan-constrained`, `proxy-constrained`, `bind-pinned`, `other`)
- strongest safe sentence
- stronger rejected sentence
- evidence freshness

Example safe sentence:

- `This pair still has direct and relay lanes configured, but only TCP and relay are presently shared in common; interface pinning is preference-only rather than hard cutoff.`

### 2) Route class card

Render rows for:

- discovery class (`tracker`, `LAN multicast`, `LAN broadcast`, `predefined hosts`, `mixed`, `unknown`)
- transfer class (`direct`, `relay`, `proxy-egress-only`, `no-common-lane`, `unknown`)
- listening dependency (`required`, `not required for current lane`, `unknown`)
- audience class (`same LAN`, `configured remote peers`, `internet-reachable`, `unknown`)

### 3) Protocol overlap card

Separate these truths explicitly:

- configured local transport protocols
- configured remote transport protocols
- common transport overlap
- tracker protocol posture
- blocked-by-no-common-protocol risk
- route fallback if overlap disappears

### 4) Cipher overlap card

Show:

- configured local cipher set
- configured remote cipher set
- effective common cipher overlap
- LAN encryption posture (`forced`, `not forced`, `unknown`)
- stronger blocked sentence if encryption assumptions exceed evidence

### 5) Bind and fallback card

Show:

- bind posture (`unbound`, `preferred-interface`, `hard-interface-cutoff`, `unknown`)
- selected interface witness
- fallback behavior if interface disappears (`switch-to-next-active`, `refuse-to-connect`, `unknown`)
- proxy effect on incoming reach (`incoming blocked`, `mixed`, `unknown`)

### 6) Proof ceiling and next-safe action rail

Only show actions that preserve meaning, such as:

- `Open protocol overlap review`
- `Open bind witness review`
- `Open transport hardening review`
- `Emit transport profile lineage receipt`

## Rules

### Rule 1 — configured set may not impersonate effective overlap

The page must keep `I allowed these protocols` separate from `these peers still share these protocols in common`.

### Rule 2 — interface preference and hard cutoff must stay separate

A chosen interface is not yet a hard boundary unless disappearance also blocks fallback.

### Rule 3 — route class and crypto class stay separate

A direct route with weak overlap assumptions is not the same truth as a relay route with stronger overlap.

### Rule 4 — strongest safe sentence must remain explicit

The page must say the most that can honestly be claimed now and preserve the stronger claim that is still blocked.
