# Remedy-runway contract sheet page — priority, headroom, source readiness, and response window

## Purpose

This page is the operator's compact contract for whether a named case can actually execute a cure now, rather than merely preserving the ingredients for some future attempt.
It exists so the product can distinguish `the repair lane survives somewhere` from `the repair lane is executable for the required cohort inside the promised window`.

## Core fields

- case identifier
- source hold-enforcement receipt identifier
- current remedy-runway posture rung
- requested cure objective
- required cohort
- response-window requirement
- latest safe-start time
- source-required objects
- source-present objects
- source-missing objects
- placeholder-only objects
- ghost or no-source risk posture
- execution lane priority class
- preemption rights
- competing workload summary
- scheduler or pause constraints
- upload headroom posture
- download headroom posture
- temporary space requirement posture
- active queue depth
- active internal-task pressure
- watcher or discovery lag risk
- manual steps still required
- strongest blocked stronger cure sentence
- next strengthening trigger
- next weakening trigger

## Remedy-runway posture rungs

The page must model at least these distinct rungs:

- cure requested only
- cure runnable with manual preparation
- cure runway partial
- cure runway ready for named cohort
- cure runway ready for required cohort
- cure runway degraded by queue or headroom risk
- cure runway blocked by source absence
- cure runway missed or expired
- cure execution suspended intentionally
- remedy-runway collapsed

## Required distinctions

The page must keep these truths separate:

- preserved bytes versus source-present bytes
- placeholder visibility versus actual downloadable source presence
- priority configured versus effective execution runway
- scheduler-open window versus sufficient response window
- free space currently above threshold versus enough temporary write headroom for the needed repair
- connected-cohort runway versus required-cohort runway
- automatic execution rights versus manual-only execution lane

## Operator promises

The contract sheet must let the operator say things like:

- `repair substrate exists, but the required source peer is offline, so runway remains blocked by source absence`
- `priority is configured, but competing work and internal merge pressure keep remedy only manual-runnable rather than ready-now`
- `the required files are visible as placeholders only, so runway is weaker than downloadable readiness`
- `disk threshold is not red, but patched restore still lacks safe temporary-space headroom`
- `desktop cohort is runway-ready, but mobile cohort is still outside the executable cure lane`

## UI behavior

The page must visually scar any blocked stronger sentence with the exact blocker class:

- source absence
- placeholder-only visibility
- ghost-file uncertainty
- queue saturation
- scheduler closure
- pause state
- disk headroom shortfall
- temporary write amplification risk
- discovery lag
- manual preparation debt

## Invariants

- the page never lets hold enforcement impersonate executable runway
- the page never lets priority settings impersonate actual timely forward progress
- the page never lets visible placeholders impersonate source-ready repair
- the page always states whether the runway is for named cohorts only or all required cohorts
