# Rename/move explanation page: local path change, remote replay, and archive dependence interface spec

## Purpose

This page explains the propagation semantics of a local rename or move.

It answers:

> if I rename or move this here, what happens on other seats, what byte-reuse or replay path is expected, and what dependency does that explanation have on retained history or archive state?

The page exists because `rename` is never just a cosmetic local action in a sync system.

## Core decision

Any rename or move action with remote consequences must expose a first-class **Rename / move explanation** page or drawer before or immediately after apply.

That explanation owns:

- local semantic class of the action
- whether the change is local-label-only, local-path-only, or remote-observable path content change
- expected remote manifestation
- whether byte reuse / archive replay is expected
- when retransmission is the stronger honest expectation

## Page layout

The page renders the same order:

1. action summary
2. local meaning
3. remote expectation
4. replay / transfer basis
5. risk and fallback
6. receipt

### 1) Action summary

Show:

- old local path / name
- new local path / name
- whether this is rename-only, move-only, rename+move, or relabel-only
- whether the local seat remains bound

### 2) Local meaning

Show:

- whether the stable subject changed or only the local disk name changed
- whether other peers inherit the visible title or keep their own local names
- whether the action changes arrival templates or only present bind facts

### 3) Remote expectation

Choose one or more:

- `no peer-visible rename`
- `remote replay under new name expected`
- `archive-assisted restore expected`
- `fresh transfer likely`
- `needs stronger review because continuity is weak`

The operator should never have to infer these consequences from a separate FAQ.

### 4) Replay / transfer basis

Show:

- whether retained byte history or archive makes replay likely
- whether missing retained history makes retransmission more likely
- whether path disappearance on another seat could look like delete+reappear
- whether weak chronology confidence or mixed-writer conflict could complicate the story

### 5) Risk and fallback

Show:

- whether this is safe to apply now
- whether a relocation review should happen first
- what fallback the product will choose if remote replay cannot be proven
- whether receipts will record a local-only rename versus a broader continuity event

### 6) Receipt

The receipt proves:

- action class
- local path delta
- peer-visible expectation
- replay basis verdict
- fallback chosen if the stronger path failed

## Rules

### Rule 1 — rename and relabel stay separate

A semantic title change must not be conflated with a local disk-path rename.

### Rule 2 — remote behavior must be explained where the action lives

Operators should not have to leave the action surface to understand remote replay.

### Rule 3 — retained-history dependence must be explicit

If replay quality depends on retained history or archive, say so.
`Optimized` is not enough.

## Honest outcomes

The page may conclude:

- `local-only rename`
- `remote replay expected`
- `fresh transfer more likely`
- `review relocation first`
- `history basis too weak to promise replay`

It may not flatten those into a generic success toast.
