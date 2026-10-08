# Remedy-hardening-attestation successor beneficiary-continuity timeline page — share, link, connect, detach, rebind, supersede, and withdraw events

## Purpose

This page records the life of one beneficiary-facing result from first durable custody through live subscription, detachment, local divergence, reconnect, supersession, withdrawal reach, or final narrowing.
It exists so the product can tell whether a beneficiary who got and kept the result also stayed current with the canonical successor truth.

## Required event families

The timeline must support at least these events:

- beneficiary-custody state bound
- canonical lane selected
- manual share issued
- linked-device continuity enrolled
- one-time file transfer issued
- local share attached
- local share detached or source removed
- disconnected-folder state entered
- reconnect attempted
- reconnect bound to old or new path
- local divergence or stop-updating state observed
- supersession or withdrawal event published
- correction reached beneficiary
- continuity sentence upgraded
- continuity sentence narrowed
- receipt superseded

## Event fields

Each event must preserve:

- timestamp
- actor or system source
- source world
- event family
- touched subject identifier if applicable
- before state
- after state
- whether continuity confidence widened or narrowed
- whether a stronger sentence became safe, stayed blocked, or became newly blocked
- linked evidence identifiers

## Timeline views

### Compact rail

Show only:

- beneficiary-custody state bound
- canonical lane selection
- first detachment or live-subscription event
- first continuity upgrade
- first later narrowing or supersession

### Full audit view

Show:

- every share, transfer, connect, disconnect, and reconnect event
- every local-divergence, detached-export, and topology-fragility event
- every supersession, correction, withdrawal, and sentence upgrade or downgrade

## Mandatory badges

The timeline must surface badges for:

- durable copy only
- detached snapshot
- live subscription
- reconnect pending
- path rebind
- local divergence
- correction reached
- correction missed
- topology fragile
- continuity sentence blocked
- receipt superseded

## Hard rules

The timeline must never allow:

- `durably held` to silently become `will stay current`
- `received once` to silently become `still subscribed`
- `reconnectable later` to silently become `live now`
- `recipient can share further` to silently become `future corrections will reach every branch`
