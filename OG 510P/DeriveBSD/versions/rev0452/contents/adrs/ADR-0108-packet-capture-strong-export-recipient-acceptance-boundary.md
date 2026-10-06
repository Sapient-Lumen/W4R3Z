# ADR-0108: Packet-capture stronger export recipient-acceptance boundary

- **Status:** Accepted
- **Date:** 2026-03-09
- **Deciders:** DeriveBSD archive maintainers

## Context

ADR-0104 made stronger packet-capture raw-byte export proof-bound.
ADR-0105 required explicit non-`auto` approval evidence.
ADR-0106 kept completed stronger export on the generic transport lane instead of treating a local file write as completion.
ADR-0107 then kept the stronger chain digest-stable across normalization, approval, transport, and export.

That still left one practical ambiguity:
a successful send is not always the same thing as recipient acceptance.

For ticket uploads, portal ingests, email adapters, and OOB workflows, a transport can succeed while the receiver later rejects, quarantines, or fails to surface the artifact.
That is especially important for stronger `packet.capture.normalized` exports because the whole point of the lane is to keep the handoff explainable.

## Decision

For stronger `packet.capture.normalized` export, a final packet-capture export receipt now means **recipient-accepted**, not merely **transport-attempt-succeeded**.

DeriveBSD reuses the generic transport/export lane rather than inventing a packet-only subsystem:

- `transport.receipt` still records that bytes were sent through a policy-bound handoff path.
- `transport.acceptance.receipt` records that the intended recipient-side lane accepted the same artifact.
- `packet.capture.export.receipt.profile` now requires:
  - `delivery_state = recipient-accepted`
  - `transport_acceptance_receipt_digest`
  - the acceptance receipt to stay on the same normalized artifact digest already bound by ADR-0107.

Ordinary `packet.capture.summary` export is unchanged.

## Consequences

### Positive

- The stronger lane can now distinguish “we sent it” from “the recipient-side evidence path accepted it”.
- Fleet and appliance/regulatory shapes gain a cleaner audit story for sensitive exports.
- Workstation and general-purpose shapes still keep the stronger lane viable because acceptance can be represented via ticket-visible, portal-ingest, signed-MDN, manual-OOB, or custom evidence.

### Trade-offs

- Some transports will only produce acceptance asynchronously.
- Some recipients will not echo a remote digest; DeriveBSD therefore binds acceptance to the already digest-stable local artifact plus a recipient-side reference, rather than requiring every remote system to compute a matching digest.

## What this does not decide

This ADR does **not** decide:

- exact wire protocols for acceptance polling,
- exact retry behavior for asynchronous recipient systems,
- exact transparency requirements for every transport backend,
- or whether every non-packet export class should adopt the same stricter acceptance rule immediately.

It only fixes the stronger packet-capture export boundary: final stronger export means recipient-accepted, not merely transported.
