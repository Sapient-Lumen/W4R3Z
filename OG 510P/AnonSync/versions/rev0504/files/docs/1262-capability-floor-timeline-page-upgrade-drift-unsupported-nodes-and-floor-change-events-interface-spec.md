# Capability-floor timeline page: upgrade drift, unsupported nodes, and floor-change events interface spec

## Purpose

Capability floors are not static.
They move when a member upgrades, a new member joins, a NAS node enters the cohort, a linked family splits, or an unsupported platform becomes the blocker.
This page exists to make those changes legible over time.

## Core decision

AnonSync must keep one **Capability-floor timeline** for every subject whose truthful capability claim can change because of cohort composition.

## Timeline events to preserve

Supported event kinds must include:

- `member-upgraded-major`
- `member-downgraded-or-held`
- `mixed-major-linked-family-created`
- `mixed-major-linked-family-resolved`
- `business-held-node-joined`
- `platform-floor-tightened`
- `feature-ceiling-raised`
- `feature-ceiling-lowered`
- `migration-blocker-cleared`
- `unknown-became-known`

## Entry shape

Each entry must show:

- event time
- event kind
- affected members
- old strongest safe sentence
- new strongest safe sentence
- old blocked stronger sentence
- new blocked stronger sentence
- evidence basis

## Special views

The page must support these filters:

- `show only floor-lowering events`
- `show only lane blockers`
- `show only linked-family risk events`
- `show only feature-ceiling raises`

## Hard rules

- timeline entries must preserve sentence changes, not just raw version changes
- a new blocker must name whether it is version, lane, platform, or safety based
- a cleared blocker must not erase the prior weaker period from history
