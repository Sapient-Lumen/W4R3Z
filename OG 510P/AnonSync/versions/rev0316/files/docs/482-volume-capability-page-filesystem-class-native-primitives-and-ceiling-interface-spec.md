# Volume capability page: filesystem class, native primitives, and ceiling interface spec

## Purpose

This page answers:

> what exact filesystem or volume class is carrying this subject, what primitives does it natively support, and what strongest honest ceiling follows before we call the target healthy?

The page exists because `folder exists`, `mounted`, and `writable` are not enough truth when the target volume changes what the product can really promise.

## Core rule

Every non-trivial target volume must compile to one first-class **Volume capability** page before the product treats it as a semantically ordinary subject root.
That page owns:

- filesystem / volume class
- native primitive support
- strongest capability ceiling
- portability note
- capability receipt

## Primary layout

The page always renders the same regions:

1. volume verdict
2. filesystem-class card
3. primitive-support card
4. ceiling / portability card
5. receipt and follow-on links

### 1) Volume verdict

Show:

- verdict label: `full-capability`, `limited-native`, `stub-backed`, `degraded`, `unknown`
- strongest honest one-line summary
- current target path and host seat
- one safest next action

### 2) Filesystem-class card

Show:

- normalized target path
- volume / filesystem class (`ntfs`, `fat32`, `exfat`, `apfs`, `ext4`, `cifs-smb`, `provider-backed`, `unknown`)
- whether the target is local, removable, networked, or virtualized
- how the class was learned (`probe`, `provider API`, `operator assertion`, `imported config`)
- strongest class-specific caveat

The operator must be able to answer: **what kind of target is this, really?**

### 3) Primitive-support card

Show:

- native alternate-stream support
- native xattr support
- native resource-fork support if relevant
- placeholder-affordance eligibility
- strongest unsupported or uncertain primitive

Where the answer is not binary, use explicit states such as:

- `native`
- `limited`
- `fallback-only`
- `not supported`
- `unknown`

The operator must be able to answer: **what primitives does this target honestly carry natively?**

### 4) Ceiling / portability card

Show:

- strongest honest product ceiling on this target
- whether metadata carriage is native or fallback-backed
- whether shell/materialization actions can ever be complete here
- strongest portability risk for bundles, streams, or cross-host round-trips

The operator must be able to answer: **what promise must we stop making on this target?**

### 5) Receipt and follow-on links

Link to:

- Metadata fidelity
- Affordance ceiling
- Volume repair

After any accepted action, emit a receipt that preserves:

- filesystem class before and after
- primitive support verdicts
- strongest acknowledged ceiling
- chosen next review

## Honest outputs

This page may conclude:

- `NTFS local volume · native stream support · full shell ceiling acceptable`
- `FAT32 removable volume · no native alternate streams · metadata degraded`
- `provider-backed target · native class unproven · review before strong promises`
- `network share with unknown stream support · do not claim bundle fidelity yet`

It may not collapse these into one generic `Folder connected` outcome.

## Rules

### Rule 1 — capability class must sit next to any healthy verdict

Do not let the product say `healthy`, `connected`, or `supported` without being able to reveal what volume class is underneath.

### Rule 2 — native and fallback are different states

Fallback carriage is not just a successful implementation detail.
It changes portability and repair truth.

### Rule 3 — unknown class blocks strong promises

If the product cannot prove the target class or primitive support, it must widen honesty immediately instead of borrowing confidence from the source seat.

### Rule 4 — writable is not the same as semantically complete

The target may be writable yet still unable to support the product's stronger affordances or metadata guarantees.

## Event language

Use explicit phrases such as:

- `target class is FAT32; stream fidelity cannot be native here`
- `volume class supports native streams; stronger affordances allowed`
- `capability class unknown; strong metadata promises blocked`
- `writable target accepted under degraded semantic ceiling`

Avoid vague lines such as:

- `folder ready`
- `path okay`
- `supported enough`

## Non-clone reason

Current official Resilio docs are usefully candid that filesystem and volume class matter.
But the operator still has to reconstruct that truth from xattr docs, shell troubleshooting, and hidden sidecar notes.
AnonSync should instead expose one Volume capability page where class, primitives, ceilings, and receipts stay adjacent.
