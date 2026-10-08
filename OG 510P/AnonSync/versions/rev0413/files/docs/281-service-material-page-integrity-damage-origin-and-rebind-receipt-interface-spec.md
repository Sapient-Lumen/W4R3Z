# Service material page: integrity, damage origin, and rebind receipt interface spec

## Purpose

`42`, `56`, and the earlier repair/continuity work already imply that sync state depends on more than user-visible bytes.
This document turns that into one ordinary page.

The page exists to answer one ordinary operator question:

> what service material exists for this subject, is it healthy, and can I repair it without pretending continuity survived when it did not?

## Core decision

Every subject with durable runtime material must render one first-class **Service material** page.
That page is the semantic home of:

- service-material inventory and location
- integrity and ownership verdicts
- damage origin and conflict hypotheses
- admissible repair paths
- continuity-preserving versus rebind-forcing outcomes
- receipts for material mutation or rebuild

The page must not rely on operators discovering these truths only through hidden directories or error strings.

## Primary page layout

The page always renders the same top-level regions in the same order:

1. integrity verdict strip
2. material inventory card
3. identity-bearing components card
4. damage-origin and conflict card
5. repair-path matrix
6. receipts and preserved evidence
7. destructive rebuild drawer

### 1) Integrity verdict strip

The strip shows:

- subject name
- bound seat or runtime
- one integrity verdict
- one continuity verdict
- one next-honest-action button

Allowed integrity verdicts:

- `healthy`
- `degraded but coherent`
- `missing critical material`
- `conflicting ownership`
- `foreign or duplicated material detected`

Allowed continuity verdicts:

- `continuity intact`
- `repair may preserve continuity`
- `rebind required`
- `continuity already displaced`

### 2) Material inventory card

Show typed rows for each material family, for example:

- identity-bearing service bundle
- archive / versioning store
- exclusion rules material
- partial-transfer residue
- local cache or index material
- diagnostic / evidence bundle

Each row shows:

- location or storage class
- whether it is hidden or operator-visible
- mutability class
- backup importance
- whether it survives share removal

### 3) Identity-bearing components card

This card isolates the items whose loss changes continuity semantics.
Show:

- component name
- why it is identity-bearing
- strongest healthy witness
- whether it can be reconstructed from peers
- whether reconstruction preserves continuity or only recreates capability

The page must make `recreated` visibly different from `preserved`.

### 4) Damage-origin and conflict card

Show candidate causes such as:

- accidental deletion or move
- duplicate runtimes touching the same material
- foreign runtime ownership
- partial media loss or unmounted path
- corruption after abrupt interruption
- operator-initiated purge

Each row shows:

- confidence grade
- affected components
- whether bytes, continuity, or both are at risk
- evidence used for the hypothesis

### 5) Repair-path matrix

Render ordered repair rows such as:

- `Reattach preserved material`
- `Repair path and retain continuity`
- `Quarantine foreign material and rescan`
- `Export Archive evidence, then rebuild bind`
- `Force clean rebind`

Each row shows:

- continuity class
- byte-survival result
- reversibility
- expected receipts
- prerequisites still missing

### 6) Receipts and preserved evidence

Show recent service-material receipts with:

- actor
- subject
- material family touched
- action class
- continuity outcome
- evidence bundle refs
- remaining follow-up

### 7) Destructive rebuild drawer

If continuity-preserving repair is impossible, place destructive options behind a drawer such as `Clean rebuild and new bind`.
That drawer may contain:

- discard conflicting material
- create fresh bind against same bytes
- export salvage bundle first
- keep runtime frozen until manual review

The page must state exact continuity loss before any such action becomes live.

## Narrow-width behavior

In narrow width the page may stack cards, but it may not hide:

- current integrity verdict
- continuity-preserving versus rebind-forcing truth
- identity-bearing components
- next admissible action

## Acceptance criteria

This spec is satisfied when:

- an operator can tell from one page which service material exists and which parts are continuity-bearing
- hidden runtime files are no longer the only semantic home of the answer
- damaged, missing, duplicated, and foreign-owned material are visibly different states
- repair paths state whether they preserve continuity or only recreate capability
- any committed repair or rebuild leaves a durable receipt naming the actual continuity outcome
