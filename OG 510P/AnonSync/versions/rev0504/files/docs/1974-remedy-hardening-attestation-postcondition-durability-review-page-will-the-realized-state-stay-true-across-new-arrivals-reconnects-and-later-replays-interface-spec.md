# Remedy-hardening-attestation postcondition-durability review page — will the realized state stay true across new arrivals, reconnects, and later replays?

## Purpose

This page is the operator-facing review that answers the practical durability question after postcondition realization is already good enough: given that the intended state is true now for some slice, will it stay true for the governed slice across the next governing horizon, and what is the strongest durability sentence the product may honestly publish now?

## Primary review prompts

The review must answer these prompts in order:

1. **What target postcondition is currently realized, and for which slice?**
2. **What future arrivals, reconnecting lanes, hidden devices, or delayed worlds can still re-enter that slice?**
3. **Which witnesses show the state surviving beyond first realization rather than merely appearing once?**
4. **Which hazards could re-open the old condition through replay, rescan, restore loss, path churn, or placeholder regression?**
5. **What steady-state horizon is actually covered by evidence, and what permanence language stays blocked?**
6. **What is the highest durability sentence the product may honestly say now?**

## Review sections

### 1. Realization basis board

Show:

- source postcondition-realization receipt
- target postcondition sentence
- governed slice
- currently realized class

### 2. Survivor-lane board

Show:

- future-arrival cohort
- reconnecting lanes
- hidden or cleared devices that may return
- paused or delayed lanes
- external or unlinked remnant lanes if relevant

### 3. Recurrence-hazard board

Show:

- replay or overwrite hazards
- restore or rearchive hazards
- placeholder or ghost-file hazards
- path-duplication or wrong-default-path hazards
- any recurrence budget already exceeded

### 4. Horizon board

Show:

- named steady-state horizon
- witnesses that cover that horizon
- slice that is actually covered
- broader stronger sentence that remains blocked

## Operator decisions this page must support

The review must let an operator decide among at least these outcomes:

- keep the case at realized-now-only
- certify durability for named current cohort only
- block durability because future-arrival governance is open
- block durability because reconnect or replay hazards remain live
- certify horizon-bounded durability for named slice
- certify governed-slice durability while broader permanence stays blocked

