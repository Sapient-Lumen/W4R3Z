# Execution timeline page — assent, mandate, execution, suspension, and override events

## Purpose

This page is the time-ordered event surface for how a typed act progressed from assent to possible execution.
It exists so the archive can distinguish `someone agreed` from `someone was actually authorized to carry it out now`.

## Mandatory event families

- assent recorded
- execution mandate issued
- execution mandate narrowed
- execution mandate expired
- execute-now confirmation requested
- execute-now confirmation received
- delegate appointed
- agent lane enabled
- autopilot lane enabled
- autopilot lane blocked
- execution started
- execution completed
- execution paused or aborted
- override triggered
- execution validity reopened

## Mandatory columns

- event time
- event type
- source act version
- exact effect lane
- acting identity or device
- acting actor class
- supervision posture after event
- execution mandate rung after event
- strongest sentence newly earned or newly blocked
- exact cause of widening, narrowing, expiry, override, or reopen

## Required comparisons

The timeline must keep these comparisons explicit:

- `assent recorded` vs `execution mandate issued`
- `execution mandate issued` vs `execute-now confirmation received`
- `delegate appointed` vs `delegate executed`
- `agent lane enabled` vs `autopilot lane enabled`
- `execution completed` vs `execution validity still under challenge`

## Required badges

- `assented`
- `execution-mandated`
- `execute-now-pending`
- `execute-now-confirmed`
- `delegate-lane-open`
- `agent-lane-open`
- `autopilot-lane-open`
- `autopilot-lane-blocked`
- `execution-aborted`
- `execution-validity-reopened`

## Failure modes the timeline must prevent

- collapsing assent and execution authorization into one timestamp
- losing which exact version widened or narrowed the execution mandate
- losing when automation was enabled only for a narrow lane
- implying that one earlier owner or device action permanently settles later execution rights
- forgetting when a later challenge downgraded an earlier execution sentence

## Stronger-sentence guard

The timeline may say `assent was recorded on day 1, delegate execution authority opened on day 2, a supervised agent prepared the route on day 3, fresh execute-now confirmation arrived on day 4, the human principal performed the irreversible commit on day 5, and autonomous execution remained blocked throughout`.
It may not say `full autopilot authority existed from day 1` unless every required rung and supervision row supports that stronger sentence.
