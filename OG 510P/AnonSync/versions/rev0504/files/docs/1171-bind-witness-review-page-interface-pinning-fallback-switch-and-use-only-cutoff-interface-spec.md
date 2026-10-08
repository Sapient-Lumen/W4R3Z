# Bind witness review page: interface pinning, fallback switch, and use-only cutoff interface spec

## Purpose

This page answers one ordinary question:

> when I bind this runtime to an interface, what really happens if that interface goes away?

The page exists because `prefers eth0`, `currently on eth0`, and `will not use anything else` are not the same truth.

## Core decision

Every interface-binding change must open one first-class **Bind witness review**.

The review owns:

- intended interface
- current witness
- fallback posture
- disappearance behavior
- stronger blocked sentence
- apply verdict

## Fixed page order

1. bind request header
2. current interface witness card
3. disappearance consequence card
4. fallback and residue card
5. apply verdict

### 1) Bind request header

Show:

- target runtime
- requested interface or selector
- strongest safe sentence
- stronger rejected sentence

### 2) Current interface witness card

Show:

- configured bind selector
- currently active interface witness
- operating-system dependence note where needed
- confidence that the current witness matches the request

### 3) Disappearance consequence card

Possible explicit outcomes:

- `switches to next active interface`
- `stops attempting peer connections`
- `current effect unknown until restart or link loss`

The operator must be able to answer:

> if the preferred interface vanishes, does traffic drift or stop?

### 4) Fallback and residue card

Show:

- whether `use_only_bind_interface` is active
- whether public or cross-subnet reach could reappear through fallback
- whether the current posture is preference-only or hard-cutoff
- minimum proof needed before claiming `interface-confined`

### 5) Apply verdict

Possible outcomes:

- `apply preference-only bind`
- `apply hard cutoff`
- `block; evidence too weak`
- `cancel and reopen transport profile`

## Rules

### Rule 1 — selected interface must not impersonate cutoff

A current witness on one interface is weaker than proof that other interfaces will not be used.

### Rule 2 — disappearance behavior must be explicit

The operator should know whether failure means drift or stop before accepting the bind.

### Rule 3 — interface confinement claims need proof

The page must preserve the stronger blocked sentence if fallback residue is still possible.
