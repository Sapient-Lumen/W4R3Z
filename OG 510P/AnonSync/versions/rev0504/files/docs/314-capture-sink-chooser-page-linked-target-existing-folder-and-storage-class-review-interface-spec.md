# Capture sink chooser page: linked target, existing folder, and storage-class review interface spec

## Purpose

This page answers one ordinary question:

> which sinks are actually part of this ingest relationship, how were they admitted, and what storage/path constraints change the meaning of `backed up there`?

The page exists because `selected linked devices`, `desktop target`, `manual link recipient`, and `existing-folder-only removable storage` are different sink realities, not one generic destination.

## Core decision

Every capture-only ingest relationship must render one first-class **Capture sink chooser** page.
That page owns:

- participating sinks
- sink admission route
- chosen path or storage class on each sink
- current readiness and durability class
- path/storage ceilings that affect ingest meaning

The workbench must not force the operator to mentally merge linked-device checkboxes, QR/link delivery, default-root behavior, and removable-storage caveats.

## Primary layout

The page always renders the same regions in the same order:

1. sink roster strip
2. candidate and admitted sinks table
3. storage/path constraints card
4. durability threshold card
5. sink assignment receipts

### 1) Sink roster strip

Show:

- count of admitted sinks
- count of proposed but not yet admitted sinks
- current policy threshold, for example `any one durable sink` or `all primary sinks`
- the strongest admission gap if one exists

### 2) Candidate and admitted sinks table

Each row shows:

- sink seat label
- admission route: `linked-device selection`, `manual link redemption`, `standing sink template`, `operator-added after creation`
- path/storage class
- whether the path was operator-chosen, defaulted, or platform-forced
- readiness verdict: `ready`, `degraded`, `not yet admitted`, `needs storage grant`, `existing-folder-required`
- whether the sink currently counts toward durability threshold

The operator must be able to answer: **which sinks count right now, and why?**

### 3) Storage/path constraints card

This card publishes:

- internal/sandbox/removable/provider-mediated storage classes
- whether the sink may create a new folder or must use an existing one
- duplicate or suffix risk at the chosen path
- background and filesystem ceilings on that class
- restore/history or archive ceilings if they differ by storage class

The operator must be able to answer: **what storage rule changes the meaning of landing on this sink?**

### 4) Durability threshold card

This card publishes:

- the policy threshold for `durably landed`
- which admitted sinks satisfy that threshold today
- which sinks are informational only and do not count
- what exact missing condition prevents a proposed sink from counting

The operator must be able to answer: **what sink set is enough before the product says a source item is safe under policy?**

### 5) Sink assignment receipts

Receipts show:

- sink admitted
- sink removed
- storage class changed
- path default overridden
- threshold changed
- provider grant accepted or lost

## Non-negotiable rules

### Rule 1 — sink count is not durability by itself

A list of linked devices is not the same thing as durable sink proof.
The page must identify which sinks actually count.

### Rule 2 — admission route must stay visible

A sink admitted by explicit checkbox selection is not the same as a sink that later redeemed a link or inherited a standing target template.

### Rule 3 — storage class must stay adjacent to path truth

`stored on SD` or `stored in sandbox` changes meaning.
The page must keep storage class next to path and readiness.

## Honest outputs

The page may conclude:

- `Laptop-ash and NAS-pine count; phone-preview does not count because it is local-preview only.`
- `Removable-storage sink admitted but existing-folder-only rule still applies to future relocation.`
- `Manual-link sink pending redemption; current policy threshold still unmet.`
- `Default path chosen automatically on this sink; operator has not yet reviewed collision risk.`

It may not collapse those outcomes into one generic `Backed up to 3 devices` label.
