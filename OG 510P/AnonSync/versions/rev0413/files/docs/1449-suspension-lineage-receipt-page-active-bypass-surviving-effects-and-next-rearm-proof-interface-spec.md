# Suspension lineage receipt page: active bypass, surviving effects, and next re-arm proof interface spec

## Purpose

The suspension contract, bypass review, proof page, and stop-semantic timeline carry detail.
What the archive still needs at handoff time is one compact receipt answering:

> what bypass is active or just ended, what still survived during it, and what exactly must be proven before the original control can safely be overclaimed again?

## Core decision

AnonSync must emit one **Suspension lineage receipt** whenever a stop-like override is armed, extended, expires, resumes, or restores trust.

## Required receipt fields

### Identity block

- `suspension_id`
- affected control id
- source case / rollout / maintenance id
- owner
- current suspension class
- current status

### Active-truth block

- requested stop effect
- surviving effects summary
- scope
- expiry or review deadline
- current weaker surviving sentence
- blocked overclaim

### Resume block

- resume class
- auto-resume yes/no
- resume requested or not
- next re-arm proof needed
- trust restoration pending or complete
- successor suspension if any

### Risk block

- current overstay or drift pressure
- latest same-cause escape during bypass if any
- linked reopened object if any
- next required review page
- next forbidden shortcut

## Supported compact verdict language

The receipt must support compact phrases such as:

- `paused locally; deletions and indexing still survive`
- `scheduled stop window active; uploads may still occur elsewhere`
- `network-gated on forbidden interface; new updates not detected`
- `disconnected but reconnectable; trust not restorable until reconnect proof`
- `peer access revoked; bytes remain locally but future updates are suspended`
- `resumed, but underlying control still awaits attestation`

## Hard rules

### 1) Surviving effects are mandatory

A receipt is incomplete if it says only that the control was paused or stopped.
It must say what still continued.

### 2) Resume and trust restoration stay separate

A receipt must always distinguish `can resume`, `did resume`, and `trust restored`.

### 3) Expiry pressure is mandatory while active

An active bypass receipt must say when it must be reviewed or why it can remain active.

### 4) Handoff must preserve the next shortcut to avoid

The receipt is not complete unless it records the next unsafe assumption, such as `resume does not yet restore full trust`.

### 5) Detached topology may not masquerade as a temporary pause

If the chosen stop changed path, peer relation, or reconnect state, the receipt must say so explicitly.
