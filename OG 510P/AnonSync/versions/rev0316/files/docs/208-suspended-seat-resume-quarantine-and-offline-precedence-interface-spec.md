# Suspended-seat resume, background gaps, and offline-precedence quarantine interface spec

## Purpose

The archive already had clock-authority, writer-contention, re-entry, and chronology-uncertain return language.
What it still lacked was one explicit interface contract for a narrower but very common case:

> a seat that stopped participating for platform reasons, collected local edits while effectively offline, and then comes back with changes whose chronology or authority should not silently outrank work done elsewhere.

Current official Resilio docs make this seam sharper than a generic `offline edits may conflict` warning.
They still say background synchronization is unavailable on iOS, that Android task-killers or memory optimizers can kill Sync in the background, and that every time the app is shut down and re-opened all folders are re-indexed and get a new modification time.
The same docs still warn that if a peer modified data offline and later goes online, its version takes priority over changes made by peers that remained online; a separate conflict FAQ likewise says the latest file that comes online wins, even over chronologically later online edits, with overwritten versions ending up in Archive.

That is not just ordinary conflict handling.
It is a suspended-seat precedence contract.

## Core decision

AnonSync should treat resume from a constrained or suspended seat as a first-class **chronology review point**.

If a seat returns after a background gap, process death, or explicit offline interval and carries local mutations, the product must classify resume confidence before those mutations are allowed to propagate widely.
The interface must distinguish:

- seat was continuously participating
- seat was suspended but chronology confidence remains high
- seat was suspended and local mutations require quarantine review
- seat was suspended and local mutations are explicitly allowed to override due to operator policy

## Why this matters

Current Resilio docs still reveal five interface mistakes AnonSync should not clone:

- background support differences can silently change whether a seat was actually participating in the mesh
- restart/reindex behavior can mutate precedence without one visible chronology-confidence surface
- offline-local work can outrank online work merely by arriving later, even when the user expects chronological merge logic
- archive placement of overwritten versions is not the same thing as making precedence understandable beforehand
- mobile/constrained seats can therefore carry hidden `late winner` behavior unless the interface explicitly quarantines or reviews them

AnonSync should therefore keep one stronger rule:

> late return from a suspended seat is not ordinary sync; it is a chronology claim that may require review.

## Fixed review order

Every suspended-seat return with local mutations should render the same sections in the same order:

1. **Seat execution posture**
2. **Resume confidence**
3. **Mutation precedence review**
4. **Resume receipt**

### 1) Seat execution posture

This section should show:

- whether the seat supports background participation
- whether the app/runtime was suspended, killed, or intentionally offline
- time since last confirmed participation
- whether local mutations occurred during the gap
- whether any authoritative clock or journal continuity was lost

The operator must be able to answer: **was this seat actually in the mesh while I thought it was?**

### 2) Resume confidence

This section should show:

- chronology confidence level
- reason for downgrade if any
- subjects affected
- newer remote mutations seen during the gap
- whether automatic propagation is allowed, delayed, or quarantined

The operator must be able to answer: **can these local edits safely rejoin automatically, or are they suspect?**

### 3) Mutation precedence review

This section should show options such as:

- `prefer online lineage`
- `prefer resumed-seat lineage`
- `fork both and require adjudication`
- `quarantine resumed-seat changes pending manual review`

Each option must declare:

- objects affected
- whether peers will see overwrites, forks, or temporary blocks
- whether archive/recovery points will be created
- whether the choice changes ongoing seat policy or only resolves this incident

The operator must be able to answer: **what precedence rule am I actually applying to these resumed changes?**

### 4) Resume receipt

This section should show:

- seat posture and gap classification
- chronology confidence before/after review
- precedence decision chosen
- recovery/rollback handle if created
- whether the seat remains under tightened monitoring

The operator must be able to answer: **what happened when this seat resumed, and what proof remains?**

## Main surface

The home/status surface should expose a **Suspended return** card whenever a seat comes back with local mutations after a posture gap.
It should say things like:

- `resumed seat has unreviewed offline edits`
- `background participation absent on this seat; chronology confidence reduced`
- `late return quarantined pending precedence review`
- `resumed edits accepted under local override policy`

It should never simply say `syncing` and let the operator discover later that online work was overwritten.

## Object model implications

AnonSync should add or strengthen these objects:

- `seat_execution_posture`
- `resume_gap_case`
- `chronology_confidence_assessment`
- `precedence_review`
- `resume_receipt`

Suggested fields for `resume_gap_case`:

- `seat_id`
- `gap_start`
- `gap_end`
- `background_support`
- `local_mutation_count`
- `remote_mutation_count_seen`
- `confidence_level`
- `quarantine_required`
- `recommended_precedence_options[]`

## Event language

Use explicit phrases such as:

- `seat resumed after background gap`
- `local mutations quarantined pending chronology review`
- `late return would outrank online lineage`
- `resumed-seat lineage accepted by operator review`
- `online lineage preserved; resumed changes forked`

Avoid vague lines such as:

- `device came back online`
- `changes synced`
- `conflict handled`

## CLI shape

Example commands:

```text
anonsync seat posture <seat>
anonsync resume review <seat>
anonsync resume apply <review> --prefer online
anonsync resume receipt <id>
```

The CLI must expose the same chronology-confidence and precedence choices as the local web UI.

## Failure and edge cases

### Seat lacks background support by design

The product should remember that this is normal for the seat class and should surface it as posture, not as a mysterious intermittent failure.

### Android/task-killer style interruption

The system should classify the gap as unplanned suspension and may tighten confidence if journals or watches were not continuous.

### Operator explicitly wants late return to win

That is allowed, but it must be a reviewed precedence action with a receipt and recovery handle.

## The non-clone reason

This is another clean example of why AnonSync should not merely copy Resilio's surface.
Current official Resilio docs still leave too much meaning about background gaps, restart-induced precedence, and late-return overwrite risk scattered across mobile limitation pages and conflict FAQs.
AnonSync should instead make suspended-seat return a first-class chronology review with quarantine and receipts.
