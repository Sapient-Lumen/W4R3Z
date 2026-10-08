# Profiler capture review page: purpose, cost, restart gate, and local artifact interface spec

## Purpose

A profiler run is not just `more logging`.
It changes resource cost, creates local artifacts, and often exists for a very specific question.

## Core decision

AnonSync should therefore model performance/incident instrumentation as a reviewed **profiler capture review page** before it is enabled.

The page must answer:

1. why this capture is being started
2. what extra data family will be recorded
3. what cost or perturbation is expected
4. whether restart or reproduction dwell is required
5. where the resulting artifacts will live locally

## Required sections

1. **Question being investigated**
2. **Capture contract**
3. **Resource / behavior cost**
4. **Activation gate**
5. **Local artifact placement**
6. **Stop / discard / keep outcome**

## Capture contract

Show:

- incident identifier or operator note
- intended question (`route bottleneck`, `disk stall`, `hash starvation`, etc.)
- start time
- whether this is bounded by time, reproduction event, or manual stop

## Resource / behavior cost

The page must classify potential cost:

- CPU
- memory
- disk growth
- user-visible slowdown risk
- restart requirement

Never imply that deeper capture is free.

## Activation gate

If restart is required, say so plainly.
If the product needs a minimum reproduction dwell, say how the page will mark `too short to trust`.

## Local artifact placement

Show:

- expected artifact names or family (`profiler trace`, `debug log extension`, etc.)
- storage root / hidden path class
- rotation behavior if any
- whether the operator can inspect before any send

## Outcome controls

Offer only explicit outcomes:

- enable now
- stage and restart
- defer
- discard pending capture plan

## Anti-clone rule

Do not hide profiler capture under a bare advanced checkbox with no cost or artifact explanation.
