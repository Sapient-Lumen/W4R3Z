# Remedy-flight-protection contract sheet page — preemption, interruption budget, and finish guarantee

## Purpose

This page is the operator's compact contract for whether a case that is runnable now is also realistically protected strongly enough to finish.
It exists so the product can distinguish `we can start` from `we are protected enough to finish inside the promised window`.

## Core fields

- case identifier
- source remedy-runway receipt identifier
- current remedy-flight-protection posture rung
- requested cure objective
- required cohort
- current execution cohort
- promised finish window
- latest safe-finish time
- active source set
- fragile source set
- interruption budget class
- allowed ordinary preemptors
- forbidden preemptors
- queue preemption exposure
- scheduler exposure
- pause exposure
- source-disappearance exposure
- hidden-task pressure posture
- watcher or rediscovery exposure
- service-metadata integrity posture
- temporary-write continuity posture
- restart survivability posture
- manual babysitting requirement
- strongest blocked stronger cure sentence
- next strengthening trigger
- next weakening trigger

## Remedy-flight-protection posture rungs

The page must model at least these distinct rungs:

- cure start requested
- cure started but interruptible
- cure in-flight protected for named cohort
- cure in-flight protected for required cohort
- cure preempted or requeued
- cure suspended intentionally
- cure stalled by hidden work or discovery lag
- cure aborted by source loss
- cure aborted by service-state corruption
- finish-protection collapsed

## Required distinctions

The page must keep these truths separate:

- runway ready versus started
- started versus finish-protected
- visible byte progress versus interruption-bounded finish confidence
- queue priority configured versus preemption actually bounded
- scheduler-open now versus finish window protected end to end
- source online at start versus source continuity through finish
- folder visible in the UI versus service metadata intact enough to keep syncing
- operator watching manually versus unattended finish guarantee

## Operator promises

The contract sheet must let the operator say things like:

- `the cure can start now, but higher-priority arrivals may still suspend it, so it remains started-but-interruptible`
- `the cure is in flight for the named desktop cohort, but one required mobile/source lane remains too fragile for required-cohort finish protection`
- `bytes are moving, but scheduler closure before safe-finish time keeps the stronger finish-protected sentence blocked`
- `service metadata is degraded enough that all synchronization may suspend, so start evidence cannot impersonate believable finish protection`
- `manual supervision can probably carry this cure across the line, but unattended finish protection remains blocked`

## UI behavior

The page must visually scar any blocked stronger sentence with the exact blocker class:

- higher-priority preemption
- queue rebuild churn
- scheduler closure
- pause state
- hidden-task congestion
- watcher or rediscovery lag
- source continuity fragility
- ghost-file risk
- service-metadata corruption risk
- restart or temporary-write fragility
- manual babysitting debt

## Invariants

- the page never lets runway readiness impersonate finish protection
- the page never lets started bytes impersonate bounded interruption risk
- the page never lets source presence at start impersonate source continuity to finish
- the page always states whether finish protection is for named cohorts only or all required cohorts
