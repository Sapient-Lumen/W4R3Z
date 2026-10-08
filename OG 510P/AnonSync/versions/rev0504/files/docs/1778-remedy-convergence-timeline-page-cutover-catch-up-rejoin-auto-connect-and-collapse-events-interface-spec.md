# Remedy-convergence timeline page — cutover, catch-up, rejoin, auto-connect, and collapse events

## Purpose

This page shows the event chain that turned an authoritative repair into safe cohort convergence — or failed to do so.
It exists so later readers can see where convergence weakened: placeholder-only participation, disconnected cohorts, pending auto-connect, offline-writer return, read-only suspension, or late-arrival collapse.

## Required event classes

The timeline must support events such as:

- authoritative cutover confirmed
- connected full-sync adoption confirmed
- placeholder-only cohort detected
- disconnected cohort detected
- pending or auto-connect cohort detected
- linked-device auto-availability expanded cohort
- offline writer marked as return risk
- read-only divergence suspended
- rejoin detected
- late byte adoption completed
- quarantine armed
- quarantine cleared
- returner-safe convergence completed
- future-joiner-safe convergence completed
- late-arrival overwrite detected
- convergence collapsed
- convergence verification collapsed

## Timeline rules

- every event must record actor, cohort, object, and observed convergence class
- the timeline must separate `authoritative now` from `present cohort converged` from `returner-safe` from `future-joiner-safe`
- the timeline must preserve whether weakening came from offline return, pending auto-connect, placeholder-only adoption lag, linked-device expansion, or read-only suspended divergence
- the timeline must keep manual admission and quarantine actions explicit rather than hiding them inside a final verdict

## Output sentence family

The timeline summary must support statements such as:

- `the repair cut over successfully, but disconnected and placeholder-only cohorts delayed convergence beyond the active peer set`
- `present cohorts converged cleanly, while one offline writer kept returner-safe convergence blocked until rejoin review finished`
- `future-joiner quarantine stayed active because approval memory could still auto-connect a previously pending peer`
- `the cure appeared converged briefly, then collapsed when a late-arriving peer reintroduced older state`
