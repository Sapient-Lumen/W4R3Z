# Evidence retention contract sheet page — source family, durability horizon, and proof ceiling

## Purpose

Give the operator one canonical answer to:

> what evidence families exist for this incident or subject, how long do they last, what can each one prove, and what stronger sentence is still forbidden?

This page exists specifically so the product never treats `notification seen`, `history row present`, `archive bytes found`, or `last transferred` as equivalent proof.

## Core objects shown

### 1. Claim sentence

A single human sentence at the top, for example:

- `Actor-attributed event evidence is present through History until 2026-04-21; byte witness persists longer on two peers.`
- `Byte recovery exists, but actor attribution is partial because archive evidence is not joined to retained event history.`
- `Only notification-grade evidence remains; do not infer durable authorship or full mutation lineage.`

### 2. Evidence family panel

Each family gets its own card:

- history / activity lane
- byte witness / preserved candidate
- transfer log
- notification signal
- convenience timestamp surface
- durable receipt
- external export or incident bundle

Each card publishes:

- family name
- storage locus
- retention class: `ephemeral`, `bounded`, `operator-retained`, `durable-receipt`, `unknown`
- current horizon or expiry
- strongest facts provable
- strongest blocked sentence

### 3. Proof-ceiling matrix

Rows are evidence families.
Columns are fact families:

- actor
- subject path
- mutation class
- chronology
- byte recoverability
- delivery / transfer occurrence
- current completeness / freshness relevance

Each cell must show one of:

- `proved`
- `partially proved`
- `not carried`
- `expired`
- `unknown`

### 4. Join requirements panel

Shows where stronger statements need joined evidence, for example:

- archive bytes + retained history row
- transfer log + subject receipt
- notification + later durable receipt
- convenience column + fresh verification proof

### 5. Horizon and export panel

Shows:

- next expiring family
- time to expiry
- whether export/escalation is recommended now
- what proof will be lost if nothing is done

## Required fields

- subject identifier
- incident identifier if present
- evidence family list
- durability class per family
- retention horizon per family
- proof ceiling per family
- strongest safe sentence
- stronger rejected sentence
- export recommendation

## Interaction rules

- Sorting by recency must not hide weaker durability classes.
- A visible event row must show its source family badge.
- `Seen in notifications` must never appear without a durability badge.
- If actor proof comes only from a family nearing expiry, the page must elevate that risk.
- A receipt row may summarize several families, but it must still link back to which families it joined.

## Empty / degraded states

The page must say so plainly when evidence is weak:

- `History has expired; only byte witness remains.`
- `Notification signal observed, but no durable event witness exists.`
- `Transfer timestamp remains, but actor attribution and mutation class are no longer provable.`
