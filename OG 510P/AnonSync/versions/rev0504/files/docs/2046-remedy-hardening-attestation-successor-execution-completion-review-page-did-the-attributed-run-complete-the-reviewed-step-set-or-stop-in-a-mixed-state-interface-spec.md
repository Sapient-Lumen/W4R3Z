# Remedy-hardening-attestation successor execution completion review page — did the attributed run complete the reviewed step-set or stop in a mixed state?

## Purpose

This page is the operator review surface for deciding whether the attributed execution run actually completed the reviewed step-set for the intended slice, or whether it only started, partially progressed, suspended, conflicted, ghosted, or left mixed-state residue that blocks stronger completion language.

## Questions this page must force

### 1. Reviewed completion target

- What exact step-set was the run supposed to complete?
- What counted as completion for the named slice versus the broader touched-set?
- Which residue classes were explicitly forbidden even if visible progress appeared?

### 2. Started versus completed

- Which reviewed steps actually started?
- Which steps actually finished?
- Which steps remained only queued, hashed, scanned, merged, suspended, or placeholder-only?

### 3. Background and queue effects

- Did hashing, deduplication, scanning, or merging remain in flight long enough to blur terminal state?
- Did queue suspension, active-queue rebuilding, or file-priority reshaping leave some reviewed steps unfinished?
- Did pause, rescans, or watcher exhaustion allow side effects while still blocking full completion?

### 4. Residue and contradiction

- Were any placeholders left where bytes were required?
- Did any files enter conflict state?
- Did any ghost-file expectation remain because no source peer still had the announced bytes?
- Did any stronger completion sentence become unsafe after later contradiction?

### 5. Sentence discipline

- What is the strongest honest sentence now?
- Which stronger completion sentence remains blocked?
- What proof would be required to upgrade that sentence safely?

## Required layout

### Header

Show:

- action name
- execution-run identifier
- current completion verdict
- terminal disposition if known
- current strongest safe sentence

### Left column — reviewed versus actual step-set

Show a compact comparison of:

- reviewed steps versus started steps
- started steps versus completed steps
- reviewed beneficiary slice versus actually completed slice
- reviewed residue budget versus actual residue
- required bytes-present conditions versus placeholder-only conditions

### Right column — mixed-state risks

Show:

- hazards that stayed inactive
- hazards that became evidenced
- resumable versus non-resumable partial states
- conflicts, ghosts, and other contradiction points
- whether the run is complete, partial, suspended, contradicted, or unknown

### Footer decision rail

The footer must expose:

- complete / partial / suspended / contradicted / unknown
- terminal disposition settled / open
- strongest honest sentence now
- strongest blocked stronger sentence now

## Prohibited shortcuts

The review must reject reasoning like:

- `the run fired, so the run completed`
- `the folder is visible, so the bytes landed`
- `the warning was hidden, so the residue is gone`
- `the queue is still active, so all required work is still safe to assume`
- `only a few files conflicted, so the reviewed step-set still counts as complete`

## Strong-sentence discipline

The page must block stronger sentences such as:

- this reviewed run completed as reviewed
- the intended bytes are present for the intended slice
- no partial residue remains
- no conflict or ghost risk survived
- completion is settled and final

unless the supporting terminal-disposition, residue, and contradiction fields are actually present.
