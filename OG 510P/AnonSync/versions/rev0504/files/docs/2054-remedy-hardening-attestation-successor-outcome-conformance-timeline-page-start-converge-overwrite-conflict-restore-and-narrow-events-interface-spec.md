# Remedy-hardening-attestation successor outcome conformance timeline page — start, converge, overwrite, conflict, restore, and narrow events

## Purpose

This page records the life of one attributed execution from reviewed intended result through convergence, overwrite, restore, invalidation, conflict, bounce-back, confirmation, contradiction, supersession, or withdrawal.
It exists so the product can tell whether the observed completed run actually landed the reviewed result class or only a narrower substitute outcome.

## Required event families

The timeline must support at least these events:

- reviewed result bound
- run completed
- timestamp winner selected
- pre-populated merge surplus observed
- read-only revert applied
- read-only deletion restored
- read-only add left unsynced
- invalidation raised
- archive version restored
- archive bounce-back observed
- conflict artifact created
- result-match evidence added
- collateral budget exceeded
- conformance sentence upgraded
- conformance sentence narrowed
- receipt superseded

## Event fields

Each event must preserve:

- timestamp
- actor or system source
- source world
- event family
- touched subject identifier if applicable
- before state
- after state
- whether conformance confidence widened or narrowed
- whether a stronger sentence became safe, stayed blocked, or became newly blocked
- linked evidence identifiers

## Timeline views

### Compact rail

Show only:

- reviewed result bound
- first result-shaping divergence
- first conformance upgrade
- first contradiction or collateral overrun
- supersession if any

### Full audit view

Show:

- every overwrite, restore, invalidation, merge, and conflict event
- every result-equivalence upgrade or downgrade
- every collateral-budget judgment change
- every sentence upgrade or downgrade

## Mandatory badges

The timeline must surface badges for:

- completed run
- timestamp-selected winner
- overwrite landed
- restore landed
- unsynced local residue
- conflict residue
- merge surplus
- collateral over budget
- conformance sentence blocked
- receipt superseded

## Hard rules

The timeline must never flatten:

- `run completed` into `reviewed result matched`
- `winner selected` into `intended winner selected`
- `file restored` into `reviewed meaning restored`
- `folder converged` into `collateral budget satisfied`
- `same end-looking tree` into `same reviewed outcome`
