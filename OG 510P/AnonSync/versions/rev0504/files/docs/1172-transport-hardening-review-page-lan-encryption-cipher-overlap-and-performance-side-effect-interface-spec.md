# Transport hardening review page: LAN encryption, cipher overlap, and performance side effect interface spec

## Purpose

This page answers one ordinary question:

> if I harden transport now, what overlap remains and what side effects am I knowingly accepting?

The page exists because `encrypt LAN`, `narrow cipher set`, and `compress stream` are not pure security labels; they can also change compatibility and performance.

## Core decision

Every transport-hardening mutation must open one first-class **Transport hardening review**.

The review owns:

- hardening intent
- common cipher overlap
- lane compatibility impact
- performance side effects
- strongest safe sentence
- apply verdict

## Fixed page order

1. hardening intent header
2. cipher overlap card
3. LAN transport protection card
4. side-effect card
5. apply verdict

### 1) Hardening intent header

Show:

- requested hardening action (`force-LAN-encryption`, `narrow-cipher-set`, `enable-compression`, `mixed`, `unknown`)
- scope
- strongest safe sentence
- stronger rejected sentence

### 2) Cipher overlap card

Show:

- configured local cipher set
- configured remote cipher set
- effective overlap after change
- compatibility risk if overlap becomes empty or narrower than assumed

### 3) LAN transport protection card

Show:

- LAN encryption posture before and after
- whether the stronger claim is `forced on LAN` or merely `still encrypted in ordinary session negotiation`
- route classes affected by the hardening action

### 4) Side-effect card

Show:

- slower sync risk
- higher CPU usage risk
- delayed upload risk for compression delay thresholds
- compatibility loss risk if peers no longer share overlap

### 5) Apply verdict

Possible outcomes:

- `apply hardening with shared overlap intact`
- `apply with slower-sync warning`
- `block; overlap would be lost`
- `cancel and reopen protocol overlap review`

## Rules

### Rule 1 — hardening and compatibility stay separate

The page must not imply that a stricter posture remains usable unless overlap survives.

### Rule 2 — LAN encryption claim must stay scoped

`LAN encrypted` must stay distinct from broader route or audience claims.

### Rule 3 — performance sacrifice must be named

If a hardening change may slow sync or increase CPU, the dominant side effect must be explicit before apply.
