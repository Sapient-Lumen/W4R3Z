# Packet-capture stronger export digest-stability boundary

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** operability, isolation  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate  

`docs/514-packet-capture-export-proof-chain-and-profile-posture-boundary.md` already made stronger packet export proof-bound.
`docs/515-packet-capture-strong-export-approval-evidence-boundary.md` then fixed who approved the stronger act.
`docs/516-packet-capture-strong-export-transport-boundary.md` fixed how the approved stronger act actually left.
This doc fixes the next coherence gap:
**how do we prove that normalization, approval, transport, and export all stayed about the same stronger artifact instead of four receipts that merely rhyme?**

See also:
- ADR: `adrs/ADR-0107-packet-capture-strong-export-digest-stability-boundary.md`
- packet-capture export proof-chain boundary: `docs/514-packet-capture-export-proof-chain-and-profile-posture-boundary.md`
- packet-capture stronger export approval evidence boundary: `docs/515-packet-capture-strong-export-approval-evidence-boundary.md`
- packet-capture stronger export transport boundary: `docs/516-packet-capture-strong-export-transport-boundary.md`
- packet-capture export receipt profile: `spec/packet.capture.export.receipt.profile.schema.json`
- packet-capture export consent request profile: `spec/packet.capture.export.consent.request.profile.schema.json`
- packet-capture export transport receipt profile: `spec/packet.capture.export.transport.receipt.profile.schema.json`
- packet-capture export transport acceptance receipt profile: `spec/packet.capture.export.transport.acceptance.receipt.profile.schema.json`
- packet-capture redaction receipt: `spec/redaction.receipt.packet-capture.schema.json`

## Why this needs a hard decision

The archive already says stronger packet export must be:

- normalized before ordinary promotion,
- proof-bound on the generic export lane,
- explicitly approved by a real actor,
- and transport-bound rather than local-file folklore.

But one practical ambiguity still costs too much:

- `redaction-receipt` can prove which normalized bytes were produced,
- `consent.request` can name an artifact digest,
- `transport.receipt` can name an artifact digest,
- `export.receipt` can name an artifact digest,
- yet nothing in the archive explicitly says those digests must remain the same for the stronger packet-export act.

That is too weak.
A stronger packet export needs a typed answer to **did all these receipts stay about the same bytes?**

## Accepted boundary

Across all profiles:

- `packet.capture.summary` remains the ordinary export class,
- `packet.capture.normalized` remains the stronger explicit raw-byte class,
- the stronger export chain stays on the existing redaction / consent / transport / export substrates,
- and the stronger chain must be **digest-stable**.

This means DeriveBSD does **not** add a packet-capture-only chain object.
Instead, it fixes one narrow rule over the existing fields:
**the normalized output digest anchors the stronger action, and later approval / transport / export receipts must keep pointing at that same digest.**

## Canonical digest-stable chain

For stronger `packet.capture.normalized` export, the archive now treats the packet-capture `redaction-receipt` output as the anchor artifact.
The chain is coherent only when all of these line up:

1. ``redaction-receipt`` `output_digest`
2. `consent.request.action.artifact_digest`
3. `transport.receipt.artifact.digest`
4. `transport.acceptance.receipt.artifact.digest`
5. `transport.acceptance.receipt.acceptance.remote_artifact_digest`
6. `export.receipt.artifact.digest`

The supporting-evidence chain still joins back to:

- `packet.capture.session`
- `packet.capture.summary`
- `content.import.receipt`
- `redaction-receipt`

But the new hard decision is that those joins are no longer enough by themselves.
The stronger action must also stay digest-stable across approval, transport, recipient acceptance, and final export.
Every receipt in that stronger chain should still talk about the same normalized digest rather than merely related stronger artifacts. The remote-side closure cut after that then tightens recipient acceptance too: `acceptance.remote_artifact_digest` must echo the same normalized digest rather than merely a plausible remote object reference (`docs/520-packet-capture-strong-export-recipient-digest-confirmation-boundary.md`).

## What changed in the canonical examples

The packet-capture stronger-export examples now demonstrate a real coherent chain rather than disconnected placeholders:

- the packet-capture redaction receipt points at the actual packet-capture redaction-transform digest,
- the safe-open import receipt points at that same redaction evidence,
- the consent request names the normalized artifact digest,
- the consent receipt carries the actual digest of the consent request,
- the transport receipt names the same normalized artifact digest,
- and the export receipt joins the actual consent / transport / supporting evidence digests.

That is the practical implementation cut here:
**the archive’s canonical example no longer lets implementers accidentally treat “approved some related capture” as good enough.**

## Product-shape meaning without a new knob

This decision intentionally reuses the existing profile posture and does not add a packet-specific product key.

| Profile | Ordinary packet-capture export | Stronger normalized raw-byte export digest posture |
|---|---|---|
| **A fleet_host** | brokered summary-first export | brokered stronger action must stay digest-stable from normalization to handoff |
| **B workstation** | trusted-UI-visible summary-first export | trusted-UI-visible stronger action must keep the approved and delivered bytes identical |
| **C general_os** | Derive-managed summary-first export preferred | explicit adapter use stays acceptable only when the stronger proof chain still names the same digest |
| **D appliance_factory** | minimal/redacted summary-first export | high-assurance stronger export remains digest-stable and audit-ready instead of ticket folklore |

So A–D stay coherent without forking:
packet capture does not get a new approval or transport family; it just makes the existing evidence family stricter about byte identity for the stronger class.

## Review guidance

When reviewing stronger packet-capture export changes, ask:

1. Is `packet.capture.summary` still the ordinary export path?
2. If `packet.capture.normalized` leaves the system, does the stronger chain stay digest-stable from redaction output through approval, transport, recipient acceptance, and export?
3. Does `consent.request.action.artifact_digest` match `transport.receipt.artifact.digest` and `export.receipt.artifact.digest`?
4. Does `consent.receipt.request_digest` actually verify against the joined consent request?
5. Do the joined session / summary / import / redaction evidence objects still explain the same stronger artifact rather than a related-but-different derivative?

## Why this is worth locking now

This is not another packet-only subsystem.
It is a small coherence cut that makes the existing stronger packet-export lane materially easier to implement correctly:

- A keeps oncall/export review about the same bytes,
- B keeps user-visible stronger sharing from drifting into “approved one file, sent another”,
- C keeps compatibility explicit without letting adapters quietly change the artifact mid-flight,
- D keeps the regulatory story about exactly which normalized capture left the boundary.

That is enough practical progress for this iteration.
The next closure cut then makes final stronger handoff recipient-accepted rather than merely transported (`docs/518-packet-capture-strong-export-recipient-acceptance-boundary.md`).

Last updated: 2026-03-09r249