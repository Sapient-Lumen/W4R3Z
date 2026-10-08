# Remedy-hardening-attestation successor execution provenance timeline page — bind, fire, auto-widen, substitute, and contradict events

## Purpose

This page records the life of one attempted execution from bound preview through actual fire, background participation, widening, substitution, contradiction, or supersession.
It exists so the product can tell whether the observed outcome came from the reviewed lane, an aided lane, a widened lane, a substitute lane, or a still-ambiguous mix.

## Required event families

The timeline must support at least these events:

- commit token issued
- execution watcher armed
- run fire requested
- manual fire observed
- system fire observed
- linked-device auto-arrival occurred
- remembered approval reused
- pending folder auto-connected
- start-time rescan fired
- scheduled rescan fired
- pause-residue side-effect propagated
- actual actuator diverged
- touched-set widened
- reviewed lane match confirmed
- attribution ambiguity raised
- substitute lane confirmed
- post-run contradiction discovered
- receipt superseded

## Event fields

Each event must preserve:

- timestamp
- actor or system source
- source world
- event family
- before state
- after state
- whether attribution confidence widened or narrowed
- whether a stronger sentence became safe, stayed blocked, or became newly blocked
- linked evidence identifiers

## Timeline views

### Compact rail

Show only:

- bind
- fire request
- actual fire
- widening or substitution if any
- contradiction or supersession

### Full audit view

Show:

- every automatic behavior that became relevant
- every world or lane ambiguity
- every widening or substitute indication
- every sentence upgrade or downgrade

## Mandatory badges

The timeline must surface badges for:

- manual fire witnessed
- system fire witnessed
- automatic widening risk
- substitute-lane risk
- sibling-world risk
- attribution ambiguous
- reviewed lane matched
- reviewed lane contradicted
- stronger attributable-execution sentence blocked

## Hard rules

The timeline must never flatten:

- `run requested` into `run fired`
- `run fired` into `reviewed lane matched`
- `reviewed lane matched so far` into `no widening happened`
- `no contradiction yet` into `attribution settled`
- `same end state` into `same causal path`
