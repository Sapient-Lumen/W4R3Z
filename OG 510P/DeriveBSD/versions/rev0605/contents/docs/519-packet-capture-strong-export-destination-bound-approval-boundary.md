# Packet-capture stronger export destination-bound approval boundary

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace  

`docs/515-packet-capture-strong-export-approval-evidence-boundary.md` already fixed *who* approved stronger packet raw-byte export.
`docs/516-packet-capture-strong-export-transport-boundary.md`, `docs/517-packet-capture-strong-export-digest-stability-boundary.md`, and `docs/518-packet-capture-strong-export-recipient-acceptance-boundary.md` then fixed how the approved stronger act left, stayed on the same bytes, and actually reached recipient-side acceptance. `docs/520-packet-capture-strong-export-recipient-digest-confirmation-boundary.md` tightens that closure further so recipient acceptance must echo the same normalized digest too, and `docs/521-packet-capture-strong-export-remote-object-continuity-boundary.md` keeps the same remote object id pinned through transport, recipient acceptance, and final export evidence.
This doc fixes the remaining recipient-drift gap:
**what proves that the approved stronger export went to the same destination identity that was actually approved?**

See also:
- ADR: `adrs/ADR-0109-packet-capture-strong-export-destination-bound-approval-boundary.md`
- packet-capture stronger export approval evidence boundary: `docs/515-packet-capture-strong-export-approval-evidence-boundary.md`
- packet-capture stronger export transport boundary: `docs/516-packet-capture-strong-export-transport-boundary.md`
- packet-capture stronger export recipient-acceptance boundary: `docs/518-packet-capture-strong-export-recipient-acceptance-boundary.md`
- packet-capture stronger export recipient-digest confirmation boundary: `docs/520-packet-capture-strong-export-recipient-digest-confirmation-boundary.md`
- consent UX contract: `docs/256-consent-ux-contract.md`
- packet-capture export consent request profile: `spec/packet.capture.export.consent.request.profile.schema.json`
- packet-capture export receipt profile: `spec/packet.capture.export.receipt.profile.schema.json`

## Why this needs a hard decision

The archive already says stronger packet export must be:

- explicitly approved by a real actor,
- transported through a policy-bound handoff lane,
- digest-stable across normalization, approval, transport, acceptance, and export,
- and only final once the recipient-side lane accepted the artifact.

But one expensive ambiguity still remained:

- the stronger approval request named the bytes,
- yet it did not strongly enough name the intended recipient identity,
- so a workflow could still approve one destination in human terms and deliver the same bytes to a different ticket, alias, or recipient lane.

That is too weak.
A stronger raw-byte export needs a typed answer to **which recipient identity was actually approved**.

## Accepted boundary

Across all profiles:

- `packet.capture.summary` remains the ordinary export class,
- `packet.capture.normalized` remains the stronger explicit raw-byte class,
- stronger raw-byte export still reuses the generic `consent.request` / `consent.receipt` / `transport.receipt` / `transport.acceptance.receipt` / `export.receipt` substrate,
- but the stronger approval request is now **destination-bound** as well as artifact-bound.

This means DeriveBSD does **not** invent a packet-capture-only recipient workflow.
Instead, it fixes one narrow extra rule on the existing lane:
**stronger packet export approval now approves these bytes to this destination tuple, not these bytes in the abstract.**

## Canonical typed approval-request destination binding

The generic `consent.request` schema now permits `action.destination` metadata for export-like approvals.
The packet-capture export consent request profile then makes that binding concrete for stronger packet export:

- `action.kind = export`
- `action.policy_digest` is required
- `action.artifact_digest` is required
- `action.lease_id` is required
- `action.destination.type` is required
- `action.destination.recipient` is required
- ticket-shaped stronger export also requires `action.destination.ticket_id`

When present, `action.destination.domain` and `action.destination.uri_hint` carry the intended external handoff identity in the same approval object.

That is the actual hard decision here:
**approval of stronger packet export now binds the recipient/ticket/domain tuple that later transport, acceptance, and export evidence must keep.**

## Continuity rule across the stronger chain

For stronger `packet.capture.normalized` export, the approved destination tuple and the executed destination tuple must now stay aligned across:

1. `consent.request.action.destination`
2. `transport.receipt.destination`
3. `transport.acceptance.receipt.recipient`
4. `export.receipt.destination`

This does not require every backend to use the exact same field names on the wire.
It does require DeriveBSD’s typed evidence objects to normalize those backend details back into the same recipient identity.

So the stronger chain is now explicit about two kinds of continuity at once:

- byte continuity (the same normalized digest, including `acceptance.remote_artifact_digest`), and
- recipient continuity (the same approved destination tuple).

## Why this is the right coherence cut

This is deliberately small.
It does **not** require a new approval service or a packet-only transport adapter.
It only refuses to let stronger packet export drift from “Alice approved export to vendor case CASE-8841” into “the same bytes went somewhere else but the receipts still look locally fine.”

That keeps A–D coherent without forks:

- A keeps fleet escalation bound to the intended vendor or case rather than a generic uploader target,
- B keeps trusted-UI stronger sharing explicit about *where* the bytes are going,
- C keeps compatibility adapters viable without letting aliases or helper scripts silently rewrite the recipient,
- D keeps factory/regulatory packet export tied to the approved external dossier rather than a loosely equivalent mailbox or portal lane.

## Research note

This boundary borrows a practical lesson from MDN-style receipt systems that distinguish the sender’s intended recipient from the final correlated recipient identity.
RFC 3798 defines both `Original-Recipient` and required `Final-Recipient` fields so MDNs can be correlated on a per-recipient basis.
AS2 then tightens the same idea for HTTP business exchange and says the original and final recipient values should match and must not be aliases or mailing lists.
DeriveBSD does not copy those wire formats directly, but the evidence model should keep the same discipline for stronger packet export approval.

Last updated: 2026-03-21r352
