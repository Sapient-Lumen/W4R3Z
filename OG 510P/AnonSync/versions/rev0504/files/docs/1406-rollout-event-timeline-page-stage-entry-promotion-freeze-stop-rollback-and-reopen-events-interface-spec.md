# Rollout-event timeline page: stage entry, promotion, freeze, stop, rollback, and reopen events interface spec

## Purpose

Rollouts are not static.
They move through canary, pilot, broad, freeze, rollback, and reopened states.
This page exists to make those changes legible over time.

## Core decision

AnonSync must keep one **Rollout-event timeline** for every policy rollout whose truthful sentence can change because of staged promotion, newly armed blockers, or rollback.

## Timeline events to preserve

Supported event kinds must include:

- `rollout-created`
- `subjects-classified-into-rings`
- `canary-started`
- `pilot-started`
- `broad-started`
- `promotion-blocked`
- `freeze-triggered`
- `holdback-created`
- `rollback-started`
- `rollback-completed`
- `reopen-after-remediation`
- `strongest-safe-sentence-changed`

## Entry shape

Each entry must show:

- event time
- event kind
- affected rings
- affected subject count
- old strongest safe sentence
- new strongest safe sentence
- old blocked stronger sentence
- new blocked stronger sentence
- evidence basis

## Special views

The page must support these filters:

- `show only freezes and stops`
- `show only promotions`
- `show only rollbacks`
- `show only sentence changes`
- `show only holdback changes`

## Hard rules

- timeline entries must preserve sentence changes, not just status codes
- a freeze event must name the stop class that armed it
- a rollback event must preserve rollback class and continuity truth
- reopening after remediation must not erase the prior frozen or rolled-back period from history
