# Availability witness gossip (AWG)

**Track:** A (Deployable core)


## Goal
Detect suppression of availability artifacts:
- parity failures
- outage attestations
- unreachability proofs

Even if an attacker can prevent some audiences from fetching official artifacts, gossip can spread compact hashes.

## Mechanism
Participants exchange `AvailabilityGossipMessage` objects:
- latest ATL checkpoint
- recent outage attestation hashes
- recent parity report hashes

See `schemas/AvailabilityGossipMessage.json`.

## Normative requirements
- **MUST** define peer sets and gossip interval.
- **MUST** anchor detected divergence into ATL.
- **MUST** publish AWG parameter choices (peer degree, cadence).