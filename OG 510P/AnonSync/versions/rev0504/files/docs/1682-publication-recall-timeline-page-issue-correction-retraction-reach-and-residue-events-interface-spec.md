# Publication-recall timeline page — issue, correction, retraction, reach, and residue events

## Purpose

This page is the time-ordered event surface for how a published act was later corrected, narrowed, or withdrawn across different audiences.
It exists so the archive can distinguish `the current surface changed` from `the recall actually reached the audiences that matter and left only the residue the system admits`.

## Mandatory event families

- original publication issued
- publication widened
- publication exported or mirrored
- correction proposed
- correction issued
- withdrawal issued
- audience reached
- audience acknowledged
- audience unreachable recorded
- reliance narrowed
- public summary withdrawn
- audit-only preservation activated
- residue risk downgraded
- full clawback denied

## Mandatory columns

- event time
- event type
- source publication version
- affected audience class
- recall class in force
- reach status after event
- reliance status after event
- residue class after event
- stronger sentence newly earned or newly blocked
- exact cause of widening, narrowing, residue preservation, or blocked clawback

## Required comparisons

The timeline must keep these comparisons explicit:

- `correction issued` vs `correction reached`
- `withdrawal issued` vs `withdrawal acknowledged`
- `future use blocked` vs `historic residue removed`
- `audit trace preserved` vs `public publication still live`
- `partial audience reach` vs `global recall complete`

## Required badges

- `publication-live`
- `correction-pending`
- `withdrawal-live`
- `reach-partial`
- `reach-complete`
- `acknowledged`
- `unreachable-audience`
- `reliance-narrowed`
- `audit-only`
- `residue-survives`
- `clawback-blocked`

## Failure modes the timeline must prevent

- collapsing publication change and audience reach into one moment
- losing the distinction between a correction and a withdrawal
- implying that a later clean surface means prior residue disappeared
- forgetting when unknown or unreachable audiences kept stronger claims frozen
- confusing audit preservation with ongoing ordinary publication

## Stronger-sentence guard

The timeline may say `the correction issued on day 2, all named participants were reached by day 3, public-summary withdrawal remained only partially reached through day 5, and audit-only trace stayed preserved throughout`.
It may not say `recall complete on day 2` unless every audience and residue row supports that stronger sentence.
