# Remedy-hardening-attestation successor execution completion timeline page — fire, start, apply, stall, resume, abort, and finish events

## Purpose

This page records the life of one attributed execution from fire through phase progress, suspension, queue rebuild, contradiction, completion, supersession, or withdrawal.
It exists so the product can tell whether the observed run cleanly finished, partially finished, stalled in a resumable way, or terminated with residue that blocks stronger completion language.

## Required event families

The timeline must support at least these events:

- run fire observed
- reviewed step started
- placeholder created
- byte hydration started
- byte hydration completed
- background hash started
- merge started
- queue suspended
- queue rebuilt
- watcher exhaustion detected
- periodic rescan fired
- pause-residue side effect propagated
- conflict created
- ghost-file warning raised
- reviewed step completed
- terminal disposition reached
- contradiction discovered
- resume attempted
- run superseded

## Event fields

Each event must preserve:

- timestamp
- actor or system source
- source world
- event family
- reviewed step identifier if applicable
- before state
- after state
- whether completion confidence widened or narrowed
- whether a stronger sentence became safe, stayed blocked, or became newly blocked
- linked evidence identifiers

## Timeline views

### Compact rail

Show only:

- fire
- first reviewed step start
- first blocking stall or contradiction
- first terminal disposition
- supersession if any

### Full audit view

Show:

- every started and completed reviewed step
- every placeholder-only or bytes-present transition
- every queue suspension or rebuild
- every conflict, ghost, or contradiction point
- every sentence upgrade or downgrade

## Mandatory badges

The timeline must surface badges for:

- run started
- run partial
- run suspended
- bytes still missing
- placeholder-only residue
- conflict residue
- ghost residue
- terminal disposition known
- completion sentence blocked
- receipt superseded

## Hard rules

The timeline must never flatten:

- `run fired` into `reviewed steps started`
- `reviewed steps started` into `reviewed steps completed`
- `terminal disposition open` into `still probably complete`
- `resume possible` into `no blocking residue`
- `same end-looking folder` into `same reviewed completion result`
