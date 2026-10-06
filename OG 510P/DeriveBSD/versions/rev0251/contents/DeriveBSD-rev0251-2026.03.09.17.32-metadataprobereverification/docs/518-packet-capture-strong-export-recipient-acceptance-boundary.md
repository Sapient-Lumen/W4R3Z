# Packet-capture stronger export recipient-acceptance boundary

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** operability, isolation  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace  

`docs/514-packet-capture-export-proof-chain-and-profile-posture-boundary.md` already made stronger packet export proof-bound.
`docs/515-packet-capture-strong-export-approval-evidence-boundary.md` fixed who approved the stronger act.
`docs/516-packet-capture-strong-export-transport-boundary.md` fixed how the approved stronger act actually left.
`docs/517-packet-capture-strong-export-digest-stability-boundary.md` kept the stronger chain about the same normalized bytes.
This doc fixes the next closure gap:
**when is a stronger packet export actually done rather than merely sent?**

See also:
- ADR: `adrs/ADR-0108-packet-capture-strong-export-recipient-acceptance-boundary.md`
- packet-capture export proof-chain boundary: `docs/514-packet-capture-export-proof-chain-and-profile-posture-boundary.md`
- packet-capture stronger export transport boundary: `docs/516-packet-capture-strong-export-transport-boundary.md`
- packet-capture stronger export digest-stability boundary: `docs/517-packet-capture-strong-export-digest-stability-boundary.md`
- policy-constrained transports: `docs/255-policy-constrained-transports.md`
- packet-capture export transport acceptance receipt profile: `spec/packet.capture.export.transport.acceptance.receipt.profile.schema.json`
- packet-capture export receipt profile: `spec/packet.capture.export.receipt.profile.schema.json`
- stronger export destination-bound approval boundary: `docs/519-packet-capture-strong-export-destination-bound-approval-boundary.md`

## Why this needs a hard decision

The archive already says stronger packet export must be:

- normalized before ordinary promotion,
- explicitly approved by a real actor,
- transported through a policy-bound handoff lane rather than a local file drop,
- and digest-stable across redaction, approval, transport, and export.

But one practical ambiguity still costs too much:

- `transport.receipt` can prove that bytes were sent,
- yet a recipient-side system can still reject, quarantine, or fail to surface them later,
- and the archive still has no crisp answer for whether that means the stronger export really completed.

That is too weak.
A stronger raw-byte export needs a typed answer to **did the recipient-side handoff lane actually accept the artifact?**

## Accepted boundary

Across all profiles:

- `packet.capture.summary` remains the ordinary export class,
- `packet.capture.normalized` remains the stronger explicit raw-byte class,
- stronger raw-byte export still reuses the generic transport/export substrate,
- but a final stronger packet export now means **recipient-accepted**, not merely **transport-succeeded**.

This means DeriveBSD does **not** invent a packet-capture-only delivery subsystem.
Instead, it adds one narrow extra step on the existing lane:
a stronger packet export may be transported first, but it only reaches a final export receipt after a typed recipient-acceptance receipt joins the same normalized digest.

## Canonical typed acceptance receipt profile

The archive now carries `spec/packet.capture.export.transport.acceptance.receipt.profile.schema.json`.

It stays a constrained profile over the new generic `transport.acceptance.receipt` kind and fixes the minimum shape of recipient-side closure evidence that is good enough for stronger packet export:

- `artifact.kind = packet.capture.normalized`
- `transport_receipt_digest` is required
- `outcome = accepted`
- `acceptance.remote_reference` is required
- `acceptance.remote_artifact_digest` is required
- and the acceptance receipt must keep that `remote_artifact_digest` on the same normalized bytes already named by redaction / approval / transport / export evidence.

This keeps the acceptance substrate generic while making the stronger packet lane explicit about closure. The next coherence cut also keeps that closure about the same approved recipient identity, and the newer remote-side digest-confirmation cut refuses to treat recipient acceptance as canonical unless the recipient-side receipt echoes the same normalized digest too (`docs/519-packet-capture-strong-export-destination-bound-approval-boundary.md`, `docs/520-packet-capture-strong-export-recipient-digest-confirmation-boundary.md`).

## Export-receipt join rule

The packet-capture export receipt profile now requires these additional facts when `artifact.kind = packet.capture.normalized`:

- `delivery_state = recipient-accepted`
- `transport_acceptance_receipt_digest`

That is the actual hard decision here:
**transport success is intermediate evidence; final stronger packet export requires recipient acceptance evidence.**

The stronger chain is now:

1. bounded packet-capture session,
2. typed packet-capture summary,
3. safe-open import receipt when stronger foreign artifacts were involved,
4. deterministic redaction receipt proving the normalized `packet-records-only` output,
5. explicit consent receipt proving a real actor approved the stronger export,
6. transport receipt proving the approved artifact left through a policy-bound lane,
7. transport acceptance receipt proving the recipient-side lane accepted the same artifact,
8. export receipt proving the final stronger export and naming the joined evidence.

## Why this is the right coherence cut

This is deliberately narrow.

It does **not** require every recipient system to expose a new packet-only API.
It does require the stronger lane to recover a digest-confirming receipt somehow if it wants to count recipient acceptance as canonical.
That may come from the remote system directly or from a trusted adapter that can prove the same accepted bytes.

That keeps A–D viable without forks:

- A keeps vendor/support escalation about a bounded accepted artifact instead of a best-effort upload hope,
- B keeps trusted-UI-visible stronger sharing honest about whether the recipient-side lane actually surfaced the file,
- C keeps compatibility adapters possible without pretending upload success equals recipient acceptance,
- D keeps the appliance/regulatory story about what left and what was accepted much tighter.

## Research note

This boundary borrows a practical lesson from transport protocols that distinguish send success from verified receipt.
HTTP `202 Accepted` is intentionally noncommittal and does not guarantee the request will eventually be acted upon.
And AS2 explicitly separates transfer response from signed receipt/MDN semantics, including a MIC over the received content when stronger non-repudiation is required.
DeriveBSD does not copy those wire formats directly, but it should keep the same conceptual separation in its evidence model.

Last updated: 2026-03-09r250