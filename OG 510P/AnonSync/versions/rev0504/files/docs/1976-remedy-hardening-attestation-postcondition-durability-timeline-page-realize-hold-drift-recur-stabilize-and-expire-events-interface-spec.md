# Remedy-hardening-attestation postcondition-durability timeline page — realize, hold, drift, recur, stabilize, and expire events

## Purpose

This page is the ordered event view for durability questions after postcondition realization is established.
It exists so later operators can see whether the case moved from first realization into horizon-bounded stability, or whether future arrivals, reconnects, hidden returners, pause-side effects, replay, restore loss, or path churn re-opened the hazard.

## Event classes

The timeline must support at least these events:

- source realization receipt imported
- steady-state horizon defined
- first survival observation recorded
- repeated favorable observation recorded
- future-arrival cohort expanded
- reconnecting lane re-entered
- hidden device returned
- paused-lane side effect observed
- replay or overwrite threat raised
- restore attempted
- restore survived rescan
- restore lost on rescan or replay
- ghost or placeholder regression observed
- duplicate-path or wrong-default-path recurrence observed
- named-slice durability confirmed
- governed-slice durability confirmed
- broader permanence sentence blocked
- durability expired or superseded

## Required columns

- timestamp
- event class
- source evidence or observation reference
- resulting postcondition-durability class
- stronger durability sentence newly allowed or newly blocked

## Hard rules

The timeline must never collapse:

- first realization and later survival
- hidden-device cleanup and actual retirement
- reconnect observed and reconnect-safe
- restore happened and restore survived
- current calm and horizon coverage

