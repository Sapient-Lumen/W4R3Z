# Return-to-protection lineage receipt page: re-arm class, residual delta, and blocked stronger sentences interface spec

## Purpose

The return contract, readiness review, proof page, and reconciliation timeline carry detail.
What the archive still needs at handoff time is one compact receipt answering:

> what kind of return happened, what structural delta still remains, and what exactly must be proven before the stronger pre-bypass sentence is safe to say again?

## Core decision

AnonSync must emit one **Return-to-protection lineage receipt** whenever a bypass ends, a reconnect lands, a merge return is accepted, a new baseline replaces the old one, or trust is restored after requalification.

## Required receipt fields

### Identity block

- `return_id`
- affected suspension id
- affected control or subject id
- owner
- chosen return class
- current return status

### Restoration-truth block

- target restoration intent
- motion restored yes/no
- current strongest safe sentence
- stronger sentence still blocked
- old baseline restored or successor baseline adopted
- next required review page

### Structural-delta block

- path result
- placeholder/full-byte result
- permission/topology result
- merge result if any
- accepted intentional deltas
- risk if delta persists

### Requalification block

- trust restored yes/no
- latest proof class
- next proof still required
- reopened linked object if any
- next forbidden shortcut

## Supported compact verdict language

The receipt must support compact phrases such as:

- `resumed in place; same path confirmed; trust restored`
- `reconnected; new path accepted; old sentence replaced by successor sentence`
- `connected to existing directory; merge under review; trust still pending`
- `permission restored; future updates resumed; attestation still required`
- `motion back, but placeholder posture changed; parity claim blocked`
- `activity restored, baseline replaced, stronger old equivalence claim retired`

## Hard rules

### 1) Motion and parity stay separate

A receipt is incomplete if it says only that syncing resumed.
It must say whether the return recreated the same protected state, an accepted successor state, or neither.

### 2) Residual delta is mandatory unless none truly remains

A receipt must always distinguish `no structural delta`, `accepted delta`, and `unresolved delta`.

### 3) Trust restoration must name its proof

If trust returned, the receipt must identify which proof or review allowed that stronger sentence.

### 4) Handoff must preserve the next shortcut to avoid

The receipt is not complete unless it records the next unsafe assumption, such as `motion resumed does not prove same-path parity`.

### 5) New baseline adoption may not masquerade as exact restoration

If the operator accepted a successor state instead of recreating the old one, the receipt must say so explicitly.
