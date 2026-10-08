# Remedy-runway timeline page — request, queue, preempt, start, stall, and miss events

## Purpose

This timeline records how a case moved from preserved repair substrate toward actual remedy execution readiness.
It exists so later readers can see whether runway was really available in time or only appeared favorable in snapshots.

## Event families

The timeline must support at least these event classes:

- cure requested
- required cohort changed
- response window armed
- source appeared
- source disappeared
- placeholder-only fallback detected
- ghost-file or no-source warning raised
- priority elevated
- competing workload preempted
- queue stall detected
- scheduler window opened
- scheduler window closed
- pause applied
- pause lifted
- headroom check passed
- headroom check failed
- cure execution started
- cure execution stalled
- cure execution resumed
- cure window missed
- runway collapsed

## Timeline invariants

- every event must preserve the time-authority basis used for deadline truth
- source disappearance must not be rewritten away once later sources return
- queue or headroom stalls must stay visible even if the case later succeeds
- missed windows must remain visible even if a later cure attempt works under a weaker sentence

## Derived summaries

The page must automatically derive:

- longest continuous runnable window
- total blocked time by blocker class
- latest safe-start time that remained honest
- first time required-cohort runway became true
- whether that stronger sentence later weakened, expired, or collapsed
