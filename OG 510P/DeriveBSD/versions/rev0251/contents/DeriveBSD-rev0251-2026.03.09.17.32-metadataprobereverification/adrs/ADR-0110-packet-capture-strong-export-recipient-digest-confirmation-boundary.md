# ADR-0110: Packet-capture stronger export recipient-digest confirmation boundary

- **Status:** Accepted
- **Date:** 2026-03-09
- **Deciders:** DeriveBSD archive maintainers

## Context

ADR-0107 kept stronger `packet.capture.normalized` export digest-stable across local normalization, approval, transport, and final export evidence.
ADR-0108 then separated recipient acceptance from mere transport success, and ADR-0109 bound the stronger approval to the intended recipient tuple.

That still left one practical ambiguity:
recipient acceptance could name the same recipient and a plausible remote reference, yet still fail to echo back the identity of the exact normalized artifact that was accepted.

A stronger packet export could therefore look fully receipted while the recipient-side lane only proved “something became visible in CASE-8841”, not “this exact normalized capture became visible there”.

## Decision

For stronger `packet.capture.normalized` export, recipient acceptance is now **digest-confirming** as well as recipient-bound.

DeriveBSD still reuses the generic `transport.acceptance.receipt` substrate rather than inventing a packet-only receipt type:

- the packet-capture acceptance profile now requires `acceptance.remote_artifact_digest`,
- that remote digest must equal the same normalized digest already named by redaction / approval / transport / export evidence,
- `acceptance.remote_reference` remains required so operators still know where the recipient-side system surfaced the artifact,
- ordinary `packet.capture.summary` export is unchanged.

In other words, stronger packet export acceptance now means **this recipient accepted these bytes**, not merely **this recipient accepted something**.

## Consequences

### Positive

- The stronger lane can now prove remote-side byte continuity instead of only local byte continuity plus recipient identity.
- Fleet and appliance/regulatory shapes gain a tighter audit story for vendor or regulator uploads that must later be correlated to a specific normalized artifact.
- Workstation and general-purpose shapes still keep the stronger lane viable because the extra field is just digest metadata on the existing acceptance receipt.

### Trade-offs

- Some recipient systems do not expose a stable digest for accepted attachments. Those systems are no longer good enough for canonical stronger `packet.capture.normalized` acceptance unless an adapter can compute or recover an equivalent digest-confirming receipt.
- This stricter rule is only fixed for stronger packet export today; generic transport acceptance remains looser.

## What this does not decide

This ADR does **not** decide:

- whether every non-packet stronger export class should require remote digest confirmation immediately,
- exact polling or reconciliation behavior for recipient systems that expose delayed digests,
- or how to map remote object-version histories beyond the single accepted artifact digest.

It only fixes the stronger packet-capture boundary: recipient acceptance must now confirm the same normalized digest that the rest of the stronger chain already carries.
