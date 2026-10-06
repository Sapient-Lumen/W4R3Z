# ADR-0109: Packet-capture stronger export destination-bound approval boundary

- **Status:** Accepted
- **Date:** 2026-03-09
- **Deciders:** DeriveBSD archive maintainers

## Context

ADR-0105 required explicit non-`auto` approval evidence for stronger `packet.capture.normalized` export.
ADR-0106 then kept completed stronger export on the generic transport lane rather than treating a local file write as completion.
ADR-0107 kept the stronger chain digest-stable, and ADR-0108 separated recipient acceptance from mere send success.

That still left one practical ambiguity:
approval named the bytes, but not strongly enough the intended destination identity.

A stronger packet export could therefore be approved as an abstract act and later delivered to a different ticket, recipient handle, or domain while still looking locally well-receipted.
That is exactly the kind of quiet recipient drift the archive is trying to prevent.

## Decision

For stronger `packet.capture.normalized` export, approval is now **destination-bound** as well as artifact-bound.

DeriveBSD still reuses the generic consent / transport / export substrate rather than inventing a packet-only approval subsystem:

- `consent.request.action.destination` is now the authoritative intended destination tuple for stronger packet export approval.
- The packet-capture export consent request profile requires `destination.type`, `destination.recipient`, and transport-specific fields such as `ticket_id` when the handoff class is ticket-shaped.
- `transport.receipt`, `transport.acceptance.receipt`, and `packet.capture.export.receipt.profile` must keep the same destination identity for the approved stronger act.
- Ordinary `packet.capture.summary` export is unchanged.

In other words, stronger packet export approval now approves **these bytes to this destination**, not just **these bytes somewhere**.

## Consequences

### Positive

- The stronger lane can now prove recipient continuity as well as byte continuity.
- Fleet and appliance/regulatory shapes gain a tighter audit story for which outside case or recipient actually got the stronger artifact.
- Workstation and general-purpose shapes still keep the stronger lane viable because the destination tuple is metadata only; it does not require new wire protocols.

### Trade-offs

- Some backends will only expose partial destination metadata. In those cases, DeriveBSD binds what it can prove (recipient, ticket id, domain, or URI hint) and keeps the rest as adapter detail.
- Existing generic consent requests remain optional on destination metadata; the stricter binding is only fixed for stronger packet export today.

## What this does not decide

This ADR does **not** decide:

- whether every non-packet export class should adopt destination-bound approval immediately,
- exact remote attachment/version semantics after the recipient accepted the artifact,
- or exact polling behavior for recipient-side systems.

It only fixes the stronger packet-capture boundary: approval, transport, acceptance, and export must stay on the same intended destination identity.
