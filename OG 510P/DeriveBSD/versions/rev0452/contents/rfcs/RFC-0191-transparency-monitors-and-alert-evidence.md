# RFC-0191: Transparency monitors and alert evidence

## Problem

Transparency logs provide publication evidence, but they do not automatically provide *detection*.
Without monitoring:
- unexpected publications may go unnoticed
- split-view / consistency failures may be invisible
- offline verification becomes brittle

## Proposal

Introduce explicit monitoring artifacts:

- `transparency.monitor.policy` (`spec/transparency.monitor.policy.schema.json`)
- `transparency.monitor.snapshot` (`spec/transparency.monitor.snapshot.schema.json`)
- `transparency.monitor.alert.event` (`spec/transparency.monitor.alert.event.schema.json`)

Monitors should:
- prefer bundled proofs for offline verifiability
- emit typed alert events that can halt rollouts or freeze exports
- optionally participate in witness checkpoint cosigning

## Why now

We already model transparency entries for exports and releases.
Adding monitors now makes transparency a complete lane (publish → prove → watch → react) instead of an inert log pointer.

## Risks / tradeoffs

- Monitor policy needs clear defaults to avoid operational noise.
- Diversity matters: a single monitor operator is a single point of failure.

See also: `docs/259-transparency-monitors-and-witness-gossip.md`.
