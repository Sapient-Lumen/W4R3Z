# Interface-fallback proof page — bind witness, next-active switch, and bridge-only startup boundary interface spec

## Purpose

This page exists because `bind_interface` is not proof.
AnonSync should require an **Interface-fallback proof** whenever the operator wants a stronger sentence than `currently observed on interface X`.

## Proof ladder

### Rung 1 — preference only

We know:

- a requested interface was named

We do not know:

- whether it is currently effective
- whether fall-forward already happened
- whether it will continue to hold

### Rung 2 — current effective witness

We know:

- current traffic or listener evidence points to one interface

We do not know:

- whether another active interface was used recently
- whether disappearance would trigger hard stop or silent switch

### Rung 3 — cutoff witness

We know:

- hard cutoff is configured or equivalent reviewed policy exists
- disappearance of the requested interface would stop connection attempts

We still may not know:

- whether the current observation window was completely free of prior fallback

### Rung 4 — continuity window

We know:

- one named interface remained effective through a reviewed window
- no observed fall-forward occurred in that window
- startup or unusual bridge-only postures were included or ruled out

This is the strongest ordinary proof this page should surface.

## Required sections

### 1) Requested setting and fallback semantics

Show:

- requested interface
- whether the system would switch to the next active interface
- whether hard cutoff is in force

### 2) Current witness

Show:

- current effective interface
- evidence basis
- freshness of evidence

### 3) Bridge / unusual-startup boundary

Show whether the current runtime has any sign of:

- bridge-only startup
- no-network-at-start then later recovery
- service startup with wider listener audience
- unknown startup posture

The page must never hide this under a generic `network recovered` line.

### 4) Strongest safe sentence

Examples:

- `Current traffic is observed on wlan0, but fallback to another active interface remains allowed.`
- `Requested NIC eth0 is enforced as a hard cutoff; current traffic also matches eth0.`
- `Bridge-only startup or unusual interface posture may have affected availability; continuity proof is not strong enough for a stricter sentence.`

## Receipt integration

The page must emit or link one durable proof record with:

- requested interface
- current effective interface
- fallback class
- bridge/startup notes
- proof rung

## Acceptance bar

The page is good enough when a cautious operator can answer:

- whether this is only a preference, a current witness, a hard cutoff, or a continuity proof
- whether startup weirdness still weakens the claim
- what stronger claim remains blocked
