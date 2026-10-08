# Remedy-discharge timeline page — quarantine continue, release, rearm, and reclose events

## Purpose

This page shows the event chain that turned a safely converged repair into an honestly discharged case — or failed to do so.
It exists so later readers can see where discharge weakened: remembered approvals, linked-device owner spread, pending auto-connect, broad resharing exposure, partial restoration only, or later reclose.

## Required event classes

The timeline must support events such as:

- convergence confirmed
- discharge review opened
- remembered approval surface detected
- linked-device owner spread detected
- pending or auto-connect participant detected
- disconnected participant held outside discharge
- write rights restored for named cohort
- write rights restored for required cohort
- admission rights restored for named cohort
- admission rights restored for required cohort
- Standard-folder resharing exposure detected
- quarantine release requested
- quarantine release approved
- quarantine release denied
- rearm condition attached
- later widening event detected
- quarantine reclosed
- discharge collapsed
- discharge verification collapsed

## Timeline rules

- every event must record actor, cohort, object, and observed discharge class
- the timeline must separate `converged`, `writer rights restored`, `admission rights restored`, and `quarantine released`
- the timeline must preserve whether weakening came from remembered approvals, owner spread, pending auto-connect, disconnected reentry, or broad resharing rights
- the timeline must keep manual rearm and reclose actions explicit rather than hiding them inside a final verdict

## Output sentence family

The timeline summary must support statements such as:

- `the repair converged first, but discharge stayed blocked until remembered approval surfaces were explicitly fenced`
- `ordinary mutation was restored earlier than ordinary admission rights, leaving the case only partially discharged`
- `quarantine was released with rearm conditions and then reclosed when a new auto-connect surface appeared`
- `the case looked calm briefly, then discharge collapsed when owner-spread widened the ordinary surface beyond the reviewed cohort`
