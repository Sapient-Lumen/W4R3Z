# Remedy-hardening-attestation downstream audience reliance timeline page — correction published, beneficiary switched, dependents refreshed, caches expired, and audience horizon closed events

## Purpose

This timeline shows how stale reliance retires across an audience rather than at one beneficiary alone.
It exists so the operator can see when the correction was published, when the beneficiary switched, when dependents refreshed, when stale exports or caches were retired, and when the named audience boundary could honestly be treated as repaired.

## Required event types

The timeline must support at least:

- correction published
- beneficiary adopted corrected state
- beneficiary adherence horizon opened
- direct dependent refreshed
- delegated dependent refreshed
- transitive dependent inferred refreshed
- export withdrawn
- export superseded
- cache expired
- local derivative removed
- peer disconnected
- future updates revoked
- stale residue discovered
- stale residue retired
- audience horizon closed
- receipt superseded

## Interval semantics

This page must represent two different things at once:

- point events, such as `direct dependent refreshed`
- state intervals, such as `stale export still active`, `transitive audience still under-proven`, or `named audience repaired but public reach unresolved`

Intervals must not be collapsed into single dots.

## Required views

### Default chronological view

Show all events and intervals in order, with a pinned strongest honest audience-reliance sentence for the selected time.

### Fan-out view

Group the timeline by direct, delegated, transitive, and local-only dependents so the operator can see where retirement propagated and where it stopped.

### Closure view

Show only the evidence relevant to whether the audience horizon can honestly be closed as:

- beneficiary repaired only
- narrow downstream repair
- named audience repaired
- broader public sentence still blocked

## Interaction requirements

The timeline must support:

- scrubbing to any moment and seeing the strongest sentence that was honest at that time
- clicking any stale-residue interval to open the proof bundle behind it
- comparing two audience boundaries for the same correction without losing dependency labels
- collapsing beneficiary-local events so downstream retirement remains readable

## Hard rules

The timeline must never allow:

- `beneficiary switched` to occupy the same semantic lane as `named audience retired`
- a stale-residue interval to disappear merely because a later dependent refreshed
- `peer disconnected` to overwrite `copy still present downstream`
- an audience horizon to appear closed if the proof page still records unresolved residue
