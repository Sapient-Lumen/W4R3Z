# Remedy-watch-health contract sheet page — probe freshness, drill coverage, and response budget

## Purpose

This page is the operator's compact contract for whether a discharged case's relapse guard is still credible right now.
It exists so the product can distinguish `surveillance armed` from `surveillance recently probed, recently drilled, and still honest within response budget`.

## Core fields

- case identifier
- source remedy-surveillance receipt identifier
- current remedy-watch-health posture rung
- intended authoritative object identifier
- current ordinary-lane scope
- required guarded cohort
- actually probed cohort
- actually drilled cohort
- current platform blind-spot map
- current runtime blind-spot map
- current signal-family freshness map
- last successful canary-probe timestamp
- last successful end-to-end drill timestamp
- configured freshness ceiling
- configured maximum response budget
- last measured response budget
- current logging and evidence posture
- strongest blocked stronger ordinary-life sentence
- next strengthening trigger
- next weakening trigger

## Remedy-watch-health posture rungs

The page must model at least these distinct rungs:

- surveillance armed pending watch-health probe
- watch health stale
- canary probe in progress
- canary probe passed for named cohort only
- canary probe passed for required cohort
- end-to-end drill pending
- response-budget drill passed
- response-budget drill exceeded budget
- watch-health degraded by platform blind spot
- watch-health degraded by runtime blind spot
- watch-health degraded by evidence freshness lapse
- watch-health collapsed
- guarded ordinary life presently proven

## Required distinctions

The page must keep these truths separate:

- surveillance armed versus surveillance health proven
- canary probe passed versus end-to-end drill passed
- named-cohort pass versus required-cohort pass
- freshness still inside ceiling versus stale evidence
- response arrived eventually versus response arrived inside budget
- logging available for diagnosis versus guard credibility already proven
- platform blind spot versus runtime blind spot

## Operator promises

The contract sheet must let the operator say things like:

- `the case remains discharged, but the watch health is stale because the last required-cohort probe expired yesterday`
- `the required desktop cohort passed the canary probe, but the end-to-end re-fence drill has not been run inside budget, so stronger guarded-life claims stay blocked`
- `Android remains a blind lane, but a required desktop and service cohort still passed the case probe and the response budget drill last week`
- `the watch is configured and logging is available, but hidden backlog plus watcher fallback make the honest sentence only watch-health degraded`
- `ordinary life remains honestly guarded only because the named case probe, drill freshness window, and response budget all remain live`

## UI behavior

The page must visually scar any blocked stronger sentence with the exact blocker class:

- probe never run
- probe stale
- drill never run
- drill stale
- response budget exceeded
- required cohort not probed
- required cohort not drilled
- platform blind spots still live
- runtime blind spots still live
- evidence basis too weak
