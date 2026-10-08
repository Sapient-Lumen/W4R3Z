# Remedy-hardening-attestation successor beneficiary-adherence timeline page — adopted, paused, relapsed, recovered, and horizon-closed events

## Purpose

This timeline shows interval truth, not just event truth.
It exists so the operator can see when the beneficiary first adopted the correction, when the adherence claim became vulnerable, when relapse opened, when recovery happened, and when a governed horizon actually closed.

## Required event types

The timeline must support at least:

- correction published
- beneficiary saw correction
- beneficiary acknowledged correction
- beneficiary adopted corrected working state
- horizon opened
- pause started
- pause ended
- scheduler hold started
- scheduler hold ended
- delayed-detection window opened
- delayed-detection window closed
- archive restore or stale reintroduction
- offline stale comeback
- read-only divergence opened
- recovery proven
- relapse unresolved
- horizon closed
- receipt superseded

## Interval semantics

This page must represent two different things at once:

- point events, such as `adopted`
- state intervals, such as `relapse open`, `pause active`, or `currently aligned but historical gap unresolved`

Intervals must not be collapsed into single dots.

## Required views

### Default chronological view

Show all events and intervals in order, with a pinned strongest honest sentence for the selected time.

### Relapse-channel view

Group the timeline by channel so the operator can isolate:

- archive-related relapse
- offline precedence relapse
- read-only divergence
- pause or scheduler lapse
- delayed-detection gap
- alternate working-pointer relapse

### Horizon-closure view

Show only the evidence relevant to whether the governed horizon can honestly be closed as:

- adherence unproven
- recovered after relapse
- uninterrupted adherence

## Interaction requirements

The timeline must support:

- scrubbing to any moment and seeing the strongest sentence that was honest at that time
- clicking an interval to open the proof bundle behind it
- comparing two horizons for the same beneficiary without losing the relapse channel labels
- collapsing reminder or notice events so adherence incidents remain readable

## Hard rules

The timeline must never allow:

- `adopted` to occupy the same semantic lane as `horizon closed with uninterrupted adherence`
- a closed relapse interval to disappear from historical view
- current alignment to overwrite earlier lapse intervals
- a horizon to appear closed if the proof page still records unresolved blockers
