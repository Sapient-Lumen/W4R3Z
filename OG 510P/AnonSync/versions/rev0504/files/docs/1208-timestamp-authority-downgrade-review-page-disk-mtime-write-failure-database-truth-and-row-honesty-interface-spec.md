# Timestamp-authority downgrade review page — disk mtime write failure, database truth, and row honesty

## Purpose

Review any case where the product's authoritative timestamp can diverge from the timestamp visible on disk.
This page exists because `Date modified` is not always the full truth once mtime write failures or fallback options enter the picture.

## This review must distinguish

- normal aligned disk mtime and authoritative time
- transient mtime write failure still being retried
- database-only authoritative time after retry abandonment
- chronology claims that remain blocked even though a timestamp exists somewhere
- substrate/path classes that make mtime write failure more likely

## Inputs the page must collect

### Timestamp facts

- file path
- disk-visible mtime
- authoritative timestamp in product state
- whether the timestamps align
- whether alignment has ever failed for this file or substrate

### Fallback facts

- whether `ignore_mtime_assign_errors` is active
- whether Sync is still retrying mtime writes
- whether the path is on a mounted or networked substrate likely to reject attribute updates
- whether chronology or winner logic currently depends on the authoritative timestamp

### Honesty facts

- which row surfaces still display disk-visible time
- which surfaces are using authoritative time internally
- what sentence a normal operator would otherwise over-infer

## Decision ladder

### Branch 1 — aligned timestamp authority

Use this branch when disk and authoritative time match.
The page should show:

- no active downgrade
- no special row warning required
- chronology still may require separate proof

### Branch 2 — retrying mtime write failure

Use this branch when the product still wants to preserve authoritative time on disk but has not succeeded yet.
The page should show:

- retry state
- suspected substrate cause
- that disk time is presently weak evidence

### Branch 3 — database-only authoritative time

Use this branch when retry abandonment is active and the database keeps the authoritative time while disk shows `current` or otherwise divergent time.
The page should show:

- that authoritative time survives only in product state
- which surfaces must stop overclaiming from disk-visible time
- that exports or external tools may read a different story than the product row

### Branch 4 — chronology blocked anyway

Use this branch when timestamps exist but clock trust, observation weakness, or another uncertainty still blocks stronger winner language.
The page should show:

- why timestamp alignment alone is not enough
- what extra proof is still missing
- that a correct-looking time row is not convergence proof

## Required warnings

- `Disk-visible mtime may be weaker than product-authoritative time.`
- `Database-kept time is weaker than chronology certainty.`
- `Mounted or network paths can make mtime write failure structural, not accidental.`
- `External tools may read a different timestamp story than the product row.`
- `Aligned time does not by itself prove the right version won.`

## Review outputs

- timestamp-authority class
- row-honesty requirement
- substrate-risk flag
- next repair rung
- strongest safe sentence
