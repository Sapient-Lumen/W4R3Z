# Effect-direction lineage receipt page — lane basis, reverse effects, and blocked stronger sentences

## Purpose

This page answers one ordinary question later:

> what directional lane actually governed this subject on this seat, what reverse effects were allowed or blocked, and which stronger sentence did the product refuse to make?

## Core decision

Every meaningful directionality verdict must emit one durable **Effect-direction lineage receipt**.

## Receipt fields

### Header

Show:

- subject
- seat
- event type
- time
- operator intent

### Winning lane

Show:

- winning direction class: `bidirectional`, `inbound-only`, `storage-only`, `opaque-custody`, `unknown`
- basis of that class
- any rejected stronger class

### Reverse-effect verdicts

Show separate verdicts for:

- outbound edit publication
- outbound delete publication
- reverse restore publication
- onward re-share publication
- unchanged-byte serving

### Disconnect survivor class

Show:

- what would survive local disconnect
- whether survivor bytes remained live, inert, serve-eligible, or only evidence-bearing

### Strongest safe sentence

Show:

- strongest safe sentence
- stronger blocked sentence

### Reopen conditions

Show:

- what future event invalidates this receipt
- what stronger proof would be required for a stronger lane claim

## Copy rules

- Use exact lane names, not marketing aliases.
- Preserve blocked stronger sentences verbatim enough for later review.
- Never collapse `can serve` into `can publish`.
- Never collapse `recovery possible elsewhere` into `recovery possible here`.
