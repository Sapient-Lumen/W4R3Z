# Mutation durability contract sheet page — live, persisted, boot authority, and storage home

## Purpose

Show, in one durable place, the exact persistence class of a change before the operator relies on it.

This page exists to answer:

- `is this only true in the running runtime?`
- `has it been durably persisted yet?`
- `what source of truth will win on next boot?`
- `what storage home and principal own this state?`

## Required sections

### 1. Mutation header

Must show:

- target subject or subsystem
- field or policy changed
- requested value
- current live value
- current persisted value
- current boot-authoritative value

### 2. Durability ladder

Render separate rows for:

- **Live applied**
- **Persisted to storage**
- **Boot-authoritative**
- **Restart-effective**
- **Shadowed / overridden**

Each row must publish:

- verdict (`yes`, `no`, `pending`, `unknown`)
- evidence basis
- invalidators
- whether the operator may safely rely on that row for destructive/exposure-significant work

### 3. Storage home block

Must show:

- active storage home path or identifier
- owning runtime principal / service user
- identity lineage attached to that storage home
- whether a different principal or mode would see a different state world

### 4. Authority plane block

Must distinguish:

- interactive storage-backed value
- config-file authoritative value
- startup-only flag / launch parameter
- inherited baseline value
- unknown / mixed authority

### 5. Strongest safe sentence

Examples:

- `The running runtime currently reflects this value, but durable persistence is still pending.`
- `Next boot will replay config-owned authority, not the interactive value shown here.`
- `This state belongs to the current storage home and will not follow a service-user switch automatically.`

### 6. Blocked stronger sentence

Examples:

- `This change is safely permanent because it appears in the UI now.`
- `Restart will preserve this value exactly as shown.`
- `Changing service account leaves settings/identity in the same world.`

## Interaction rules

- the page must appear automatically before any action that depends on persistence stronger than `live only`
- storage-home differences must render inline, not behind secondary disclosure
- config-owned authority must be labeled as stronger plane rather than hidden in a footnote
- copied/exported summaries must preserve all three values when they differ: live, persisted, boot-authoritative

## Receipt obligations

Any receipt derived from this page must preserve:

- requested mutation
- live verdict
- persisted verdict
- boot-authoritative verdict
- storage-home identity
- strongest safe sentence
- blocked stronger sentence
