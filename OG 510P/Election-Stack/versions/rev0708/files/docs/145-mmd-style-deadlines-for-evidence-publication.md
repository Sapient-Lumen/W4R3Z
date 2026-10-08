# MMD-style deadlines for evidence publication

**Track:** A (Deployable core)


## Goal
Attackers often win by delaying the publication of “bad news” (fork proofs, drift alerts, outage attestations).

This document adapts the transparency-log idea of a **maximum merge delay (MMD)** into a set of explicit, measurable deadlines for election evidence.

## Deadlines
Define and publish the following in the ElectionParameterBundle:
- **MMD-PBB**: maximum delay from accepting a ballot to including it in a checkpoint.
- **MMD-EVID**: maximum delay to publish required evidence objects (alerts, parity reports).
- **MAAD**: maximum availability attestation delay (for outages/partitions).

## Enforcement
- If a deadline is violated, the system MUST emit a signed `DeadlineViolation` event.
- Clients/verifiers MUST treat deadline violations as integrity incidents and display them prominently.
