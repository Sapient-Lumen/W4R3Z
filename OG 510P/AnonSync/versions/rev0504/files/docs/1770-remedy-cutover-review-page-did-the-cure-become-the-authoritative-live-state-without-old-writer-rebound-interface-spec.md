# Remedy-cutover review page — did the cure become the authoritative live state without old-writer rebound?

## Decision question

This page answers one operational question:

**Did the landed cure actually become the authoritative live state for the required writer and reader cohorts — or are we still relying on unlocked editors, split-state conflicts, timestamp races, read-only reversion, or platform-specific lock behavior to keep the fix alive?**

## Review sections

### 1) Landing versus authoritative switch

The review must begin by comparing the already-proven landing result with the stronger cutover claim actually available now.
It must show:

- what landed
- where it landed
- which cohorts are expected to treat it as authoritative
- what stronger cutover sentence is still blocked

### 2) Writer-freeze audit

The page must separate:

- live lock holders
- files still open for editing
- unlocked-writer exposure
- platform lock coverage
- app-semantic lock coverage
- read-only fallback behavior

### 3) Rebound-risk audit

The page must show what can still overwrite or split the cure, including:

- latest database-time winner risk
- latest mtime winner risk
- offline return risk
- read-only invalidation and forced re-download behavior
- conflict-file creation
- rename or namespace collision risk

### 4) Cohort switch scope

The page must model which cohorts have truly switched and which remain weaker.
It must separate:

- named pilot writers
- required writer cohort
- required reader cohort
- read-only followers
- non-locking platform participants
- conflict-bearing cohorts

### 5) Highest honest sentence

The page must always conclude with one highest honest sentence from this family:

- `cutover requested`
- `landed pending writer freeze`
- `landed pending reader switch`
- `split live state detected`
- `cutover blocked by live lock holder`
- `cutover blocked by unlocked writer risk`
- `cutover blocked by timestamp-rebound risk`
- `authoritative pilot cutover`
- `authoritative required-cohort cutover`
- `cutover collapsed by conflict rebound`
- `cutover verification collapsed`

It must also name the blocked stronger sentence and why it remains blocked.

## Review invariants

- the review never lets landing impersonate authoritative cutover
- the review never lets a lock warning or its absence settle the whole writer-risk story
- the review never lets read-only convergence impersonate symmetric cutover
- the review always names the exact blocker that prevents the stronger cutover sentence
