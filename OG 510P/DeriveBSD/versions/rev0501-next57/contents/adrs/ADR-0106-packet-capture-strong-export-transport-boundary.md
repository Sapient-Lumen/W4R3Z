# ADR-0106: Stronger packet-capture raw-byte export must be transport-bound and may not complete as a local file drop

Date: 2026-03-09  
Status: Accepted

## Context

`adrs/ADR-0104-packet-capture-export-proof-chain-and-profile-posture.md` already fixed the proof chain for stronger packet-capture raw-byte export.
`adrs/ADR-0105-packet-capture-strong-export-approval-evidence-boundary.md` then fixed the approval edge: stronger `packet.capture.normalized` export must carry explicit non-`auto` consent evidence.

That still leaves one implementer-friendly escape hatch:
**what proves that the approved stronger export and the delivered stronger export are the same act, rather than a local file drop that later wanders out-of-band?**

Without a tighter boundary, an implementation can still drift into a weak compromise:

- the stronger packet export has a valid proof chain,
- a real actor approved it,
- but the completed `export.receipt` still describes only a local file destination,
- and the actual cross-boundary delivery happens later through ambient scripts, copied files, or opaque human process.

That is too weak for a stronger raw-byte export lane.
DeriveBSD already has the right generic delivery substrate: `transport.policy` and `transport.receipt`.
The next step should be a constrained packet-capture transport profile over that lane rather than a packet-only delivery subsystem.

## Decision

**A completed stronger `packet.capture.normalized` export must be transport-bound on the generic transport lane, and it may not complete as a local file drop.**

Specifically:

1. Keep delivery on the generic transport substrate.
   - Do **not** add a packet-capture-only delivery subsystem.
   - Reuse `transport.policy` / `transport.receipt` and profile them narrowly for stronger packet-capture exports.

2. Require transport evidence for completed stronger packet exports.
   - `spec/packet.capture.export.receipt.profile.schema.json` must require `transport_receipt_digest` when `artifact.kind = packet.capture.normalized`.
   - A completed stronger export must therefore join to a concrete `transport.receipt` instead of ending at a local staging artifact.

3. Disallow local-file completion for stronger packet exports.
   - The packet-capture export receipt profile must reject `destination.type = file` for `artifact.kind = packet.capture.normalized`.
   - Local file staging may still exist as subordinate local evidence, but it is not the completed stronger export act.

4. Define a constrained transport receipt profile for stronger packet exports.
   - The canonical packet-capture export transport receipt profile must remain a constrained `transport.receipt`.
   - It must bind `artifact.kind = packet.capture.normalized`.
   - It must require a concrete recipient label and a successful result.
   - Ticketing transports should carry `destination.ticket_id`; removable media and OOB flows still remain valid so A–D do not fork.

5. Keep summary export ordinary.
   - `packet.capture.summary` remains the ordinary packet-capture export class.
   - It does not gain a packet-specific transport-completion requirement beyond the generic export lane.

## Consequences

- Stronger packet-capture raw-byte export now has a typed answer to three questions:
  - *why were these bytes exportable?* → the proof chain,
  - *who approved that stronger act?* → the consent evidence,
  - *how did the approved stronger act actually leave?* → the transport evidence.
- Workstation flows can remain recipient-visible and user-mediated, while fleet/factory flows can stay ticketed, OOB-capable, and policy-bound.
- Implementations now have a narrow spec target for the delivery edge of stronger packet export.

## What this does not decide

This ADR does **not** decide:

- exact ticket/case semantics across adapters,
- exact transport backends,
- exact media-handling protocol for removable media,
- or whether every stronger packet export must also be transparently logged.

Those remain generic transport/export posture questions.
This ADR only fixes that `packet.capture.normalized` cannot be considered a completed stronger export via “we wrote a file and something else dealt with it later” folklore.
