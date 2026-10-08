# Duplicate seat collision warning page — shared state copy, same proof, and divergent runtime risk

## Purpose

Open a blocking review whenever copied state or imported identity material would let two runtimes present themselves as the same reviewed seat lineage.

This page exists to answer:

- `what exactly looks duplicated?`
- `what harm follows if both sides run?`
- `what safe exits preserve the most truth with the least damage?`

## Required sections

### 1. Collision summary strip

Must show:

- candidate local runtime
- colliding predecessor or sibling runtime
- collision class (`shared-seat-handle`, `shared-state-root`, `shared-proof-material`, `mixed`)
- current verdict (`blocked`, `inspect-only`, `retire-other-first`, `unknown`)

### 2. Duplicated-truth matrix

Rows must include:

- seat handle / certificate lineage
- state root lineage
- subject roster lineage
- approval / trust memory
- cached route/helper residue
- receipts and evidence history

Each row must say whether it is:

- `safely shareable`
- `must rebirth`
- `must narrow`
- `must not run concurrently`
- `unknown`

### 3. Risk ladder

Must explain at least these risks:

- peer ambiguity or identity confusion
- divergent local writes under one remembered lineage
- stale trust/approval reuse on the wrong machine
- support/evidence corruption about which runtime acted
- false same-seat continuity receipts

### 4. Safe exits

Must offer reviewed paths such as:

- `freeze candidate and inspect only`
- `retire predecessor then activate successor`
- `rebirth seat and import only carried-forward subjects`
- `discard copied state and start clean`

### 5. Blocked stronger sentence

Examples:

- `Because the files match, these runtimes are just the same seat in two places.`
- `We can safely run both and let the mesh sort it out.`
