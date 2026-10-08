# Remedy-hardening-attestation successor beneficiary-authority timeline page — approve, delegate, reshare, revoke, rekey, and authority-narrowing events

## Purpose

This page records the life of one beneficiary-facing result from first live continuity through evolving sovereign sets, widening approval scope, delegated sharing, revocation, re-keying, or later authority narrowing.
It exists so the product can tell not just whether updates still reach the beneficiary, but whether the reviewed canonical authority boundary still governs those updates.

## Required event families

The timeline must support at least these events:

- canonical sovereign set declared
- folder architecture selected
- owner granted
- owner removed
- peer approved
- approval remembered or widened across linked devices
- linked device added to owner surface
- share delegated further
- standard key or equivalent onward-share event observed
- permission changed
- revoke event published
- rekey or lane replacement event published
- authority sentence upgraded
- authority sentence narrowed
- receipt superseded

## Event fields

Each event must preserve:

- timestamp
- actor or system source
- source world
- event family
- touched beneficiary / actor / slice identifier
- before state
- after state
- whether authority confidence widened or narrowed
- whether a stronger sentence became safe, stayed blocked, or became newly blocked
- linked evidence identifiers

## Timeline views

### Compact rail

Show only:

- canonical sovereign declaration
- first widening event
- first delegation or onward-share event
- first revocation / narrowing event
- current strongest sentence

### Full audit view

Show:

- every approval, remembered-approval, and linked-device-spread event
- every permission and ownership mutation
- every re-share, delegation, rekey, and revoke event
- every sentence upgrade or downgrade

## Mandatory badges

The timeline must surface badges for:

- exclusive sovereign intended
- shared authority
- approval memory widened
- linked-device owner spread
- onward-share risk
- revocation power present
- canonical-authority sentence blocked
- authority later narrowed
- receipt superseded

## Hard rules

The timeline must never allow:

- `the beneficiary still syncs` to silently become `the reviewed sovereign still governs`
- `the same identity name` to silently become `the same authority boundary`
- `a change arrived and validated` to silently become `the right governor issued it`
- `a revocation exists` to silently become `revocation power stayed within the reviewed slice`
