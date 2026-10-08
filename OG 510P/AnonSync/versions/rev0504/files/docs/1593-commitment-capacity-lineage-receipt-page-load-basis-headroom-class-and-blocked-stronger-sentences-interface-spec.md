# Commitment capacity lineage receipt page: load basis, headroom class, and blocked stronger sentences interface spec

## Purpose

This receipt is the compact durable record for the final capacity truth at the moment a promise was admitted, narrowed, deferred, or blocked.

## Core decision

AnonSync must expose one first-class **Commitment capacity lineage receipt** for every capacity-governed promise decision.

## Receipt fields

The receipt must preserve:

- receipt id
- linked capacity object id
- linked proposal id
- linked authority object id
- final admission verdict
- budget class
- load posture
- headroom class
- reserve posture
- reserve integrity
- strongest admitted sentence
- strongest blocked stronger sentence
- release trigger
- proof freshness window
- receipt owner

## Required compact sections

### 1) Basis capsule

Show the minimal basis for the capacity verdict:

- evidence window used
- largest competing load considered
- largest background-work burden considered
- scheduler or throttle distortion considered
- capacity-basis class

### 2) Capacity capsule

Show:

- admitted load at decision time
- spare headroom class
- whether reserve was intact or borrowed
- whether the new promise consumed protected reserve

### 3) Ceiling capsule

Show:

- strongest safe sentence that survived
- stronger sentence blocked by capacity
- trigger that could lift the ceiling

## Hard rules

- The receipt may not collapse `allowed to promise` into `had room to promise`.
- `headroom unknown` is allowed and must remain visible if that was the honest posture.
- A stale receipt may still describe history, but it may not masquerade as current capacity truth.

## Example sentence shapes

- `At decision time this issuer had workable headroom under a hard reserve, so one narrowed checkpoint commitment was admitted while all broader delivery promises remained blocked pending release of the recovery reserve.`
- `At decision time this lane was oversubscribed, so the proposed promise was deferred; authority remained intact, but current load and protected reserve left no honest commitment room.`
