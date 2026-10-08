# Promise capacity timeline page: budget consumed, restored, throttled, and overcommit events interface spec

## Purpose

This timeline keeps capacity posture from turning into a one-shot judgement with no history.

## Core decision

AnonSync must expose one first-class **Promise capacity timeline** whenever promise load, reserve posture, or admission verdict changes over time.

## Required event classes

Supported `capacity_event_class` values:

- `budget-initialized`
- `promise-admitted`
- `promise-narrowed`
- `promise-deferred`
- `promise-blocked`
- `reserve-tightened`
- `reserve-released`
- `background-load-spike`
- `scheduler-window-opened`
- `scheduler-window-closed`
- `capacity-recalculated`
- `overcommitment-detected`
- `preemptive-throttle-applied`
- `release-trigger-landed`
- `budget-restored`

## Fixed page order

1. **Timeline header**
2. **Load-change lane**
3. **Reserve-change lane**
4. **Admission-change lane**
5. **Current posture strip**

### 1) Timeline header

Show:

- timeline id
- linked capacity object id
- linked issuer or lane id
- currently live admission posture
- next expected release trigger

### 2) Load-change lane

Each load event must show:

- promise or work object entering or leaving the envelope
- load posture before and after
- whether the change was ordinary, surge, rescue, or recovery driven

### 3) Reserve-change lane

Each reserve event must show:

- reserve class before and after
- who approved reserve spend if applicable
- what obligation the reserve was protecting
- whether reserve returned to intact state

### 4) Admission-change lane

Each admission event must show:

- requested promise
- resulting verdict
- strongest sentence admitted then
- stronger sentence blocked then
- what changed the verdict

### 5) Current posture strip

Show:

- current admitted promise count
- current headroom class
- current reserve integrity
- whether overcommitment has ever been detected in the active window
- next event most likely to improve posture

Hard rule:

The timeline may not let a later healthy interval erase a prior overcommitment or reserve violation.
Those events must remain part of lineage.
