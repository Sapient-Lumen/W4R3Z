# Remedy-cutover proof page — live writer fence, conflict risk, and switch validity

## Purpose

This page is the case proof that a landed cure did or did not become the authoritative live state.
It exists so later readers can inspect the evidence behind the cutover sentence instead of inferring it from visible files, reassuring timestamps, or one quiet period.

## Proof bundle

The proof page must preserve evidence for:

- intended authoritative object and namespace
- intended writer cohort
- intended reader cohort
- live lock-holder evidence
- unlocked-writer exposure evidence
- database-time and mtime ordering evidence
- conflict-artifact evidence
- read-only invalidation and overwrite evidence
- platform lock-coverage evidence
- application lock-semantic evidence
- pilot versus required-cohort switch evidence
- strongest honest cutover sentence
- strongest blocked stronger cutover sentence

## Proof sentence families

The page must support concise summaries such as:

- `the repair landed, but one required editor still held an open exclusive copy, so authoritative cutover remained blocked`
- `pilot writers switched successfully, while a non-locking platform cohort kept the stronger required-cohort cutover sentence blocked`
- `a .Conflict artifact and timestamp ambiguity showed split live state, so the honest sentence was cutover collapse rather than completed switch`
- `read-only followers display the repaired state, but authoritative writer-side cutover remains blocked by unlocked writer exposure`
- `database-time rules would still prefer a later rebound candidate, so landing could not yet be promoted into authoritative cutover`

## Invariants

- the proof never compresses landing, switching, and authoritative cutover into one word
- the proof never hides unlocked-writer or timestamp-rebound risk behind visible convergence
- the proof never lets read-only or follower convergence impersonate full writer-cohort cutover
- the proof always preserves the blocker that prevented the stronger cutover sentence
