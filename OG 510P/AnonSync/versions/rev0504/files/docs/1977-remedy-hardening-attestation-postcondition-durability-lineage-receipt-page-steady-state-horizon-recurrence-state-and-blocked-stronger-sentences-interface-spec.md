# Remedy-hardening-attestation postcondition-durability lineage receipt page — steady-state horizon, recurrence state, and blocked stronger sentences

## Purpose

This page is the durable one-receipt summary for postcondition durability after postcondition realization review.
It lets a later operator read one artifact and know exactly whether the target state is merely realized now, horizon-stable for a named slice, durable for the governed slice, or still blocked by future-arrival, reconnect, replay, restore, placeholder, ghost, or path-churn recurrence risk.

## Receipt fields

- receipt identifier
- postcondition-durability identifier
- source postcondition-realization receipt identifier
- target postcondition summary
- governed-slice summary
- steady-state horizon summary
- future-arrival summary
- reconnect and hidden-returner summary
- replay and overwrite summary
- restore and rearchive summary
- placeholder, ghost, or path-churn summary
- current postcondition-durability class
- highest honest durability sentence
- blocked stronger sentence
- evidence references
- issued-at timestamp

## Primary sentence block

The receipt must begin with exactly two lines:

- **Highest honest postcondition-durability sentence**
- **Blocked stronger sentence**

## Required sections

1. **What target state is already realized now**
2. **Which survivor lanes can still re-enter the governed world**
3. **Which witnesses show stability beyond first realization**
4. **Which recurrence hazards still cap the durability sentence**
5. **Why the next stronger permanence sentence is blocked**

