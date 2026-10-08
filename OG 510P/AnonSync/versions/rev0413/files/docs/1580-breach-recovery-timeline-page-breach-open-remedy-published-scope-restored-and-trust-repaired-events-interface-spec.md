# Breach recovery timeline page: breach open, remedy published, scope restored, and trust repaired events interface spec

## Purpose

This page renders the public life of a breached commitment after failure: surviving duty, downgraded or substitute remedy, checkpoints, restored scope, trust repair, re-promise eligibility, and closure.

## Event classes

Supported `recovery_event_class` values:

- `breach-opened`
- `surviving-obligation-defined`
- `full-make-good-proposed`
- `partial-make-good-published`
- `substitute-make-good-published`
- `diagnostic-checkpoint-published`
- `scope-reduced`
- `scope-restored`
- `motion-restored`
- `trust-repair-started`
- `trust-repair-blocked`
- `re-promise-gate-opened`
- `new-commitment-authorized`
- `recovery-closed`
- `permanent-downgrade-closed`

## Required columns

- timestamp
- event class
- breached sentence before
- surviving sentence after
- recovery class before
- recovery class after
- scope delta
- trust status after
- operator who approved the change

## Hard rules

- The timeline must preserve the original breached sentence even after remedy publication.
- Scope reduction and scope restoration may not be hidden inside generic recovery notes.
- `motion-restored` and `trust-repair-started` must remain visibly different events.
- `new-commitment-authorized` must link forward to the new commitment id.

## Timeline summaries

At top of page show:

- whether full original scope was ever restored
- whether recovery stayed reduced or substitute-only
- whether trust was ever fully repaired
- total number of downgraded remedy publications
- whether any new commitment was authorized
- current strongest surviving sentence

## Highlight rails

The page must visually distinguish:

- breach with no remedy yet
- diagnostic-only recovery
- partial make-good without restored parity
- substitute recovery with permanent downgrade
- full scope restored but trust not yet repaired
- trust repaired and new promise authorized
- recovery closed without re-promise
