# Remedy-hardening-attestation successor action-envelope timeline page — preview, approve, arm, execute, trip, and abort events

## Purpose

This page records the life of one execution envelope from first preview through final within-envelope completion, trip, abort, cleanup, or contradiction.
It exists so the product can tell whether runtime containment was merely designed, actually armed, tripped, recovered, or disproved.

## Required event families

The timeline must support at least these events:

- envelope drafted
- preflight diff generated
- hazard discovered
- guardrail added
- guardrail removed
- second-actor watch assigned
- envelope approved
- envelope armed
- execution started
- runtime watcher heartbeat recorded
- side-effect observed within envelope
- trip condition observed
- automatic abort started
- manual abort ordered
- abort completed
- residual overspill discovered
- cleanup completed
- within-envelope completion attested
- later contradiction discovered
- envelope receipt superseded

## Event fields

Each event must preserve:

- timestamp
- actor or system source
- affected dimension
- before state
- after state
- whether the event widened or narrowed risk
- whether a stronger sentence became safe, stayed blocked, or became newly blocked
- linked evidence or proof artifact identifiers

## Timeline views

### Compact rail

Show only:

- drafted
- armed
- started
- tripped or completed
- cleanup or supersession

### Full audit view

Show:

- every guardrail change
- every watcher assignment
- every trip
- every abort decision
- every residue discovery
- every sentence upgrade or downgrade

## Mandatory badges

The timeline must surface badges for:

- no hard-stop available
- pause is insufficient
- remembered-approval hazard present
- reconnect hazard present
- rescan hazard present
- hydration hazard present
- overspill discovered
- stronger containment sentence blocked

## Hard rules

The timeline must never flatten:

- `approved` into `armed`
- `armed` into `started`
- `started` into `completed`
- `aborted` into `clean`
- `no known overspill yet` into `no overspill`
