# Storage substrate contract sheet page: storage class, runtime identity, notification floor, and write-path boundary interface spec

## Purpose

Before an operator trusts a path, migrates it, or repairs it, they need one ordinary page that answers:

> what substrate is this on, who is actually touching it, which path namespace is authoritative, and how strong is the change-detection / lock / write-safety contract?

This page exists so `local folder`, `UNC path`, `SMB share`, `service-visible path`, and `mixed external-writer topology` do not remain support-only distinctions.

## Core decision

Every serious synced subject must open one first-class **Storage substrate contract sheet**.

The sheet owns:

- storage class
- runtime identity
- authoritative access path
- notification floor
- lock / contention grade
- write-path boundary
- strongest safe sentence
- stronger rejected sentence

## Fixed page order

1. substrate claim header
2. runtime and namespace card
3. detection and contention card
4. write-path boundary card
5. claim ceiling and next-safe action rail

### 1) Substrate claim header

Show at minimum:

- subject / folder / share name
- storage class (`local-fs`, `network-share`, `service-unc`, `virtualized-mount`, `mixed-writer`, `unknown`)
- runtime identity (`interactive-user`, `service-user`, `local-system`, `container`, `unknown`)
- authoritative access path
- notification floor (`event-driven`, `rescan-backed`, `restart-needed`, `unknown`)
- strongest safe sentence
- stronger rejected sentence

Example safe sentence:

- `This subject is currently backed by a network share reached through a service-visible UNC path; change detection is rescan-backed rather than event-driven.`

### 2) Runtime and namespace card

Render rows for:

- effective runtime identity
- storage / state directory owner
- authoritative path namespace
- alternate visible paths
- whether the operator’s current projection matches the runtime path

Each row shows:

- current value
- evidence freshness
- scope
- whether a mismatch blocks trustworthy action

### 3) Detection and contention card

Render rows for:

- filesystem notification grade
- fallback rescan cadence
- restart-needed discovery caveat
- known lock contention
- lock-holder identity known / unknown

Each row shows:

- active state
- witness basis
- operational consequence
- what stronger claim remains forbidden

### 4) Write-path boundary card

This card is mandatory.
Show:

- approved write lane(s)
- blocked or suspect write lane(s)
- external mutator classes
- path-family collisions (`direct-on-host` plus `SMB`, `mapped drive` plus `service UNC`, etc.)
- whether the topology is `safe`, `degraded`, `review-required`, or `blocked`

For each lane show:

- authority basis
- corruption / rollback risk
- whether detection quality degrades
- receipt emitted when changed

### 5) Claim ceiling and next-safe action rail

Only show actions that preserve meaning, such as:

- `Open topology review`
- `Open lock watch`
- `Migrate runtime path`
- `Approve boundary change`
- `Emit substrate receipt`

## Rules

### Rule 1 — substrate class is public, not hidden setup trivia

The operator must never have to remember from install method or troubleshooting lore what kind of storage contract they are actually standing on.

### Rule 2 — runtime identity is mandatory

If a service account or container is the real actor, the page must say so.

### Rule 3 — authoritative access path beats familiar alias

Mapped-drive labels, pretty aliases, and last-used picker paths must not outrank the runtime-visible authoritative path.

### Rule 4 — detection quality is a contract sentence

The page must say whether the subject is event-driven, rescan-backed, or weaker.

### Rule 5 — write-path boundary is explicit

The operator must see whether mixed writers are allowed, degraded, or blocked before trusting the subject.

## Acceptance criteria

A later operator can:

- tell what storage class the subject is really on
- tell which runtime identity is acting on it
- tell which path namespace is authoritative
- tell how strong change detection really is
- tell which write lanes are safe versus blocked
- tell which stronger claim is still forbidden
