# Certificate takeover impact page: removed Advanced folders, iOS delete risk, and recovery boundary interface spec

## Purpose

This page is the consequence surface for an operator who wants blast-radius proof rather than a friendly `linked` badge.
It exists to answer:

> if this seat loses its current certificate lineage, what gets removed from control surfaces, what can disappear from the filesystem, and what recovery boundary remains afterward?

## Core decision

Every serious certificate-replacement path can be opened into a first-class **Certificate takeover impact** page.

## Fixed page order

1. impact header
2. control-surface loss timeline
3. filesystem-risk card
4. recovery-boundary card
5. claim ceiling

### 1) Impact header

Show:

- current seat lineage
- incoming lineage
- proof grade
- strongest safe sentence
- stronger rejected sentence

### 2) Control-surface loss timeline

Include impact items such as:

- current certificate lineage superseded
- Advanced subjects removed from ordinary control surface
- inherited subjects populated from source lineage
- detached local residue created

### 3) Filesystem-risk card

Show what the product currently knows about:

- subjects removed from app only
- subjects preserved on disk
- subjects at stronger platform-specific deletion risk
- whether the risk is direct, derived, stale, or unknown

### 4) Recovery-boundary card

Show:

- whether reconnect / re-add / export is needed later
- whether a removed subject can be restored in place
- whether recovery is local-only or requires another seat
- what remains unprovable now

### 5) Claim ceiling

Explicitly forbid overclaim language when evidence is insufficient.
Example forbidden claims:

- `Nothing important changes except pairing`
- `All removed subjects remain safely recoverable in place`
- `This operation is fully reversible`

## Rules

### Rule 1 — takeover impact must answer `what disappears where`

A success badge alone is not enough.

### Rule 2 — app removal and filesystem removal never collapse

The page must keep those planes separate.

### Rule 3 — platform-specific stronger risk weakens optimistic language immediately

The product must degrade the sentence as soon as the stronger risk appears.
