# Remedy-hardening-attestation successor execution completion contract sheet page — reviewed step-set, terminal disposition, and partial residue

## Purpose

This page is the operator-facing contract sheet for one attributed successor-world execution run.
It exists to answer a narrow but decisive question:

**if this run fires through the reviewed lane, what reviewed step-set is supposed to complete, what terminal dispositions are allowed, and what partial residue must never be mistaken for clean completion?**

## Core decision this page must support

The page must let the product distinguish at least these states:

- bound and attributable run exists, not yet started
- run started, step-set still partial
- run progressing, background tasks active, terminal disposition still open
- run suspended but resumable inside reviewed envelope
- run partially completed with mixed-state residue
- run completed for named slice only
- run completed with contradiction hazards still live
- run terminated with conflict, ghost, or missing-source residue
- completion claim later narrowed or withdrawn

## Minimum fields

### Identity and scope

- action identifier
- successor world identifier
- source execution-provenance receipt identifier
- execution-run identifier
- reviewed actuator identifier
- reviewed beneficiary slice
- reviewed touched-set summary
- reviewed step-set summary

### Completion contract

- required completion condition summary
- named-slice completion condition
- allowed partial-progress class
- allowed suspend-and-resume class
- forbidden residue classes
- required terminal disposition evidence
- required contradiction checks before upgrade
- strongest safe completion sentence now
- strongest blocked stronger completion sentence now

### Completion hazards

- disconnected-mode visibility hazard
- selective-sync placeholder hazard
- source-peer-online dependency hazard
- pause-residue hazard
- watcher-exhaustion rescan hazard
- background hashing or deduplication delay hazard
- queue suspension or rebuild hazard
- conflict-file hazard
- ghost-file hazard

### Current disposition section

- actual started-step-set summary
- actual completed-step-set summary
- actual stalled-step-set summary
- actual residue summary
- resumability state
- contradiction state
- terminal disposition if known
- strongest safe sentence now
- strongest blocked stronger completion sentence now

## Required layout

### Header

Show:

- action name
- execution-run identifier
- completion state
- terminal disposition badge
- current strongest safe sentence

### Left column — what reviewed completion required

Show:

- reviewed step-set
- completion condition
- required proof before upgrade
- forbidden residue classes

### Right column — what can blur completion

Show:

- active hazards
- background work still live
- partial states that resemble completion
- why `it started` or `it looks present` is still weaker than completion

### Footer decision rail

The footer must expose:

- complete / partial / suspended / contradicted / unknown
- terminal disposition known / not yet known
- strongest honest sentence now
- strongest blocked stronger completion sentence now

## Hard rules

This page must never collapse:

- `started` into `completed`
- `placeholder visible` into `bytes present`
- `warning hidden` into `problem resolved`
- `queue active` into `all required steps progressing`
- `partial named-slice success` into `reviewed run completed as reviewed`
