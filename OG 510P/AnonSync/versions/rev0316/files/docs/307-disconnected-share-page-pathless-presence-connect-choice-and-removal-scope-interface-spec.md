# Disconnected share page: pathless presence, connect choice, and removal scope interface spec

## Purpose

This page owns the meaning of a known subject that currently has no local path.

It answers:

> what exactly still exists here when this share is disconnected, what future connect choices remain open, and what wider removal scope would be accepted if I remove it now?

The page exists because pathless presence is a real state, not a tiny list chip.

## Core decision

Every known subject in pathless / disconnected state must render one first-class **Disconnected share** page.

That page owns:

- why the subject is still known here
- what local path is currently absent
- what future connect choices remain open
- whether removal would be local-only, family-wide, or stronger
- what historical bind evidence remains

## Primary layout

The page renders the same regions:

1. pathless strip
2. known-subject card
3. remembered bind card
4. connect choices card
5. removal scope card
6. recent receipts

### 1) Pathless strip

Show:

- subject title
- status: `pathless presence`
- whether the subject is merely known, still claimable, pending approval, or broken after prior bind
- one next honest action

### 2) Known-subject card

Show:

- how this subject became known here
- whether it is part of the same personal constellation, an outside share, or a local derivative family
- whether a local path existed before
- whether the subject is still reachable from any live source

### 3) Remembered bind card

Show:

- last known path if any
- why it ended: operator disconnect, failed path, policy removal, capability loss, unknown
- whether reconnecting to the old path is expected to be same-lineage or needs stronger review
- receipts proving earlier bind history

### 4) Connect choices card

Show:

- `connect to old path`
- `connect to reviewed new path`
- `keep pathless`
- `claim only, no bind yet`
- `remove`

Each choice must publish whether it creates bytes now, opens a placement review, or only changes UI memory.

### 5) Removal scope card

Show:

- what disappears from this seat
- what disappears from linked seats, if anything
- whether the subject remains externally present elsewhere
- what future reconnect opportunities would be lost
- what residue or receipts remain after removal

The page must make `hide here`, `forget here`, and `remove everywhere` visibly different when the model distinguishes them.

### 6) Recent receipts

Show recent disconnect, reconnect, and removal receipts.

## Page rules

### Rule 1 — pathless is not absence

The page must prove what survives without a path: subject memory, approvals, lineage evidence, arrival options, or nothing stronger.

### Rule 2 — reconnect is a reviewed choice, not a magic button

A reconnect action may open placement or reconciliation review.
It must not silently create a default-path duplicate.

### Rule 3 — removal scope must be legible before apply

Operators should not discover only afterward that `remove` had wider scope than they meant.

## Honest outputs

This page may conclude:

- `safe to reconnect to remembered path`
- `reconnect needs review`
- `keep pathless`
- `remove only here`
- `remove from linked family`
- `blocked pending approval`

It may not compress all of those into one `Connect` or `Remove` row action.
