# Remedy-hardening-attestation successor execution provenance review page — did the reviewed bound run actually fire through the reviewed lane?

## Purpose

This page is the operator review surface for deciding whether the execution that actually happened can honestly be attributed to the reviewed bound run, or whether a background process, remembered permission, auto-connected lane, or substitute actuator produced an only superficially similar outcome.

## Questions this page must force

### 1. Bound-run identity

- Which bound preview and commit token was this run supposed to use?
- Which actor set and subsystem were allowed to fire it?
- Which actuator path was reviewed, and which nearby actuator paths were explicitly forbidden substitutes?

### 2. Fire-time source

- What actor or system source actually initiated the change?
- Did the initiating actor satisfy the required step-up and quorum at fire time?
- Did the system fire because of manual commit, remembered approval, pending auto-connect, linked-device auto-arrival, startup rescan, scheduled rescan, or another background mechanism?

### 3. Path fidelity

- Did the actual run travel through the reviewed actuator path?
- Was the same visible effect reachable through a broader or more automatic lane?
- Did any permission-lane or architecture detour produce the outcome instead?

### 4. World fidelity

- Did execution happen in the reviewed successor world?
- Did a sibling process, service world, or re-opened seat produce the effect?
- Were multiple plausible execution worlds live at once?

### 5. Sentence discipline

- What is the strongest honest sentence now?
- Which stronger attributable-execution sentence remains blocked?
- What evidence would be required to upgrade that sentence safely?

## Required layout

### Header

Show:

- action name
- execution-run identifier
- bound-preview receipt identifier
- actual initiation verdict
- current strongest safe sentence

### Left column — reviewed versus actual cause

Show a compact comparison of:

- reviewed actor set versus actual actor set
- reviewed subsystem versus actual subsystem
- reviewed actuator versus actual actuator
- reviewed world versus actual world
- reviewed touched-set versus first observed touched-set

### Right column — attribution risks

Show:

- hazards that stayed inactive
- hazards that may have fired
- unresolved ambiguity points
- substitute lanes still plausible
- whether the run is attributable, ambiguous, or contradicted

### Footer decision rail

The footer must expose:

- attributable / ambiguous / contradicted
- reviewed lane matched / substituted / unknown
- strongest honest sentence now
- strongest blocked stronger sentence now

## Prohibited shortcuts

The review must reject reasoning like:

- `the intended result happened, so the right run fired`
- `the same user was logged in, so attribution is obvious`
- `the system was paused enough, so nothing automatic could have happened`
- `there was only one likely cause, so we can stop looking`
- `the path difference is minor, so it still counts as the reviewed lane`

## Strong-sentence discipline

The page must block stronger sentences such as:

- this exact reviewed run fired
- the reviewed actor directly caused the effect
- no automatic widening participated
- the actual lane matched the reviewed lane completely
- execution provenance is settled

unless the supporting actor, process, path, and world fields are actually present.
