# Measurement receipt page — network ceiling, Sync overhead, and next safe step interface spec

## Purpose

A completed performance experiment should leave a durable interpretation artifact, not just remembered numbers.
The operator, reviewer, or later support partner needs to know what was measured, under what conditions, and what next action that actually justifies.

AnonSync should therefore publish a durable **measurement receipt page** after every serious sidecar performance run.

## Core decision

The receipt must preserve six truths:

1. the original question
2. the baseline Sync observation
3. the quiescence and benchmark conditions
4. the supported raw-capacity verdict
5. the supported comparison back to Sync behavior
6. the next safe step and what stronger claim remains forbidden

## Required sections

1. **Experiment identity**
2. **Baseline versus benchmark summary**
3. **Capacity / asymmetry verdict**
4. **Supported bottleneck statement**
5. **Approved next step**
6. **Reopen boundary**

## 1) Experiment identity

Show:

- incident or experiment id
- participant pair
- run window
- matrix rows completed
- quiescence verdict
- receipt freshness / staleness note

## 2) Baseline versus benchmark summary

Summarize:

- observed Sync transfer band before the run
- external benchmark bands by direction / transport
- whether the comparison is apples-to-apples or only directional evidence
- important workload or route caveats

## 3) Capacity / asymmetry verdict

Classify the strongest supported finding, for example:

- `raw network ceiling comfortably above Sync band`
- `raw network ceiling near Sync band`
- `directional asymmetry observed`
- `benchmark invalid for capacity claim`
- `ceiling unknown; partial matrix only`

## 4) Supported bottleneck statement

This section should publish one carefully bounded sentence, such as:

- `Network path is unlikely to be the dominant limiter under the tested pair and window.`
- `Observed Sync slowness remains consistent with raw network limitation on this pair.`
- `The run isolates a likely direction asymmetry but does not yet identify the cause.`
- `The experiment does not support a trustworthy bottleneck claim because quiescence or coverage failed.`

## 5) Approved next step

Show the smallest reviewed next move, such as:

- open performance hypothesis review
- retry with correct quiescence
- test a direct-path intervention
- inspect internal-task / disk path
- stop because no honest quick win exists

## 6) Reopen boundary

Preserve what would require the receipt to be reopened:

- route class changes
- participant pair changes
- workload-shape changes
- failed re-test
- stale benchmark age
- conflicting later evidence

## Compact rendering obligations

Any compact receipt must still preserve:

- question
- quiescence verdict
- best supported ceiling statement
- comparison verdict
- next safe step

## Anti-clone rule

Do not clone workflows where `ran iperf` becomes a floating anecdote.
AnonSync should never let a later operator say `the network looked fine` or `Sync was the issue` unless the receipt still shows the tested pair, the quieting conditions, the result bands, and the strongest still-forbidden claim.
