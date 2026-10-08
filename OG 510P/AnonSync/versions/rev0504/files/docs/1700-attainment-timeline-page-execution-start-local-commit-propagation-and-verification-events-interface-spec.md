# Attainment timeline page — execution start, local commit, propagation, and verification events

## Purpose

This page is the time-ordered event surface for how a typed effect progressed from execution into possible verified attainment.
It exists so the archive can distinguish `the act ran` from `the intended outcome truly landed where it had to`.

## Mandatory event families

- execution started
- local commit recorded
- propagation started
- connected cohort caught up
- required cohort threshold still unmet
- recipient went offline or disconnected
- placeholder-only state observed
- no-source / ghost residue observed
- hidden-task backlog detected
- watcher exhaustion detected
- manual rescan requested
- manual rescan completed
- source peer returned
- verification strengthened
- attainment sentence reopened
- attainment sentence superseded

## Mandatory columns

- event time
- event type
- source act version
- effect lane
- covered cohort after event
- uncovered cohort after event
- residue posture after event
- verification basis after event
- highest attainment sentence newly earned or newly blocked
- exact cause of strengthening, weakening, reopen, or supersession

## Required comparisons

The timeline must keep these comparisons explicit:

- `execution started` vs `local commit recorded`
- `local commit recorded` vs `propagation started`
- `connected cohort caught up` vs `required cohort complete`
- `hidden-task backlog detected` vs `verification strengthened`
- `manual rescan completed` vs `durable attainment proven`
- `earlier completion sentence issued` vs `later attainment sentence reopened`

## Required badges

- `execution-started`
- `local-commit`
- `propagation-underway`
- `connected-only`
- `required-threshold-unmet`
- `ghost-residue`
- `watcher-loss`
- `rescan-dependency`
- `verification-strengthened`
- `attainment-reopened`
- `attainment-superseded`

## Failure modes the timeline must prevent

- collapsing execution and completion into one timestamp
- losing when the system only had connected-cohort calm instead of required-cohort proof
- forgetting when watcher exhaustion or hidden tasks made earlier calm states less trustworthy
- forgetting when a ghost file or source-peer loss downgraded the completion claim
- forgetting when a later rescan or reconnect legitimately strengthened the verdict

## Stronger-sentence guard

The timeline may say `execution started on day 1, local commit was recorded on day 1, connected recipients looked caught up on day 2, watcher exhaustion forced manual rescans on day 3, source-peer return resolved a ghost residue on day 4, and verified required-cohort attainment was finally earned on day 5`.
It may not say `completion was proven on day 1` unless every required rung truly supports that stronger sentence.
