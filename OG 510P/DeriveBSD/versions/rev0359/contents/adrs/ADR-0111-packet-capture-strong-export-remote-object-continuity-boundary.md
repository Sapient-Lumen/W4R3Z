# ADR-0111: Packet-capture stronger export remote-object continuity boundary

- **Status:** Accepted
- **Date:** 2026-03-09
- **Deciders:** DeriveBSD archive maintainers

## Context

ADR-0109 bound stronger `packet.capture.normalized` export approval to the intended destination tuple.
ADR-0110 then required recipient acceptance to echo the same normalized artifact digest.

That still left one narrow but real ambiguity:
transport success, recipient acceptance, and final export evidence could all name the same bytes and recipient while still drifting across **different remote object identifiers** inside the same case or portal.

A stronger packet export could therefore look fully receipted while the archive only proved “the right recipient accepted these bytes somewhere in CASE-8841”, not “the same remote object id survived transport, recipient acceptance, and final export evidence”.

## Decision

For stronger `packet.capture.normalized` export, the proof chain is now **remote-object-continuous** as well as digest-stable and destination-bound.

DeriveBSD still reuses the generic transport / acceptance / export substrates rather than inventing a packet-only handoff system:

- `transport.receipt.result.remote_id` remains the transport-side remote object identifier when the adapter exposes one,
- `transport.acceptance.receipt.acceptance.remote_reference` must stay on that same remote object identifier for canonical stronger packet acceptance,
- `packet.capture.export.receipt.profile` now requires `adapter.remote_id` so the final export receipt also names the same remote object identifier,
- ordinary `packet.capture.summary` export is unchanged.

In other words, stronger packet export closure now means **this recipient accepted these bytes as this remote object**, not merely **this recipient accepted these bytes somewhere**.

## Consequences

### Positive

- The stronger lane can now correlate approval, transport, recipient acceptance, and final export evidence to one remote attachment/message/object id.
- Fleet and appliance/regulatory shapes gain a tighter dossier story for later support escalation, audit, and regulator correlation.
- Workstation and general-purpose shapes still keep the stronger lane viable because the extra requirement is just one more typed join on already-existing receipts.

### Trade-offs

- Some recipient systems do not expose a stable remote object id. Those systems are no longer good enough for canonical stronger `packet.capture.normalized` export unless an adapter can recover an equivalent stable id.
- Generic transport/export receipts remain looser; this strict continuity rule is fixed only for stronger packet export today.

## What this does not decide

This ADR does **not** decide:

- how every other stronger export class should model remote object ids,
- whether recipient systems must expose version histories beyond the accepted object id,
- or how to reconcile remote object replacement after the canonical accepted handoff.

It only fixes the stronger packet-capture boundary: when the adapter exposes a remote object id, transport / recipient acceptance / final export evidence must all stay on the same remote object identifier.
