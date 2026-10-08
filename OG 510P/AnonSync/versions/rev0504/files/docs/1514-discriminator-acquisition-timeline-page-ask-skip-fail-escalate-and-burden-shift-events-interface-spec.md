# Discriminator acquisition timeline page: ask, skip, fail, escalate, and burden-shift events interface spec

## Purpose

Evidence planning becomes folklore if the operator cannot later see:

- which asks were considered
- which were selected or skipped
- when burden widened
- when a channel failed
- when the route changed because of the captured fact

The **Discriminator acquisition timeline** preserves that sequence.

## Core decision

AnonSync must ship one durable timeline page for serious evidence acquisition work so later operators do not repeat expensive capture or overstate what was ever actually learned.

## Event types

Supported `event_type` values:

- `gap-opened`
- `ask-ranked`
- `ask-selected`
- `ask-skipped`
- `budget-widened`
- `channel-unavailable`
- `capture-started`
- `capture-returned`
- `capture-failed`
- `route-narrowed`
- `route-reversed`
- `ceiling-lowered`
- `escalation-approved`
- `case-rerouted`

## Fixed page order

1. **Timeline header**
2. **Burden-shift lane**
3. **Ask-attempt lane**
4. **Route-change lane**
5. **Current acquisition posture card**

### 1) Timeline header

Show:

- timeline id
- linked case id
- total asks considered
- total asks attempted
- heaviest burden actually used
- current strongest safe sentence

### 2) Burden-shift lane

Show events where the acceptable burden changed.
Each event must preserve:

- old budget
- new budget
- approver or cause
- why the shift happened
- what new asks became available

Hard rule:

A later operator must be able to tell whether a heavy capture was always allowed or became justified only after cheaper paths failed.

### 3) Ask-attempt lane

For every selected or skipped ask, preserve:

- ask id
- rank at time of selection
- why selected or skipped
- channel used
- return class
- time spent or waiting window

Hard rule:

Skipped asks are first-class events.
The product must show why they were skipped.

### 4) Route-change lane

For every returned ask, preserve:

- prior live routes
- route effect of answer
- new governing candidate or new escalation need
- strongest sentence unlocked or still blocked

Hard rule:

The timeline must keep evidence events connected to route consequences.

### 5) Current acquisition posture card

Supported `current_acquisition_posture` values:

- `still-cheap-facts-first`
- `waiting-on-selected-ask`
- `captured-enough-to-route`
- `heavier-capture-now-justified`
- `all-feasible-asks-exhausted`
- `living-with-weaker-ceiling`

Required rows:

- current acquisition posture
- next allowed ask
- next forbidden overclaim
- next rereview trigger

## Failure state

If the timeline is empty, show:

- `No evidence-acquisition history exists yet. Routing remains based on raw intake facts only.`
