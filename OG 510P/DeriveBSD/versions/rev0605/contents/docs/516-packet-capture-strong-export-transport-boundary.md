# Packet-capture stronger export transport-boundary

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace  

`docs/515-packet-capture-strong-export-approval-evidence-boundary.md` already fixed the approval edge for stronger packet-capture raw-byte export.
This doc fixes the next execution-facing gap:
**what proves that the approved stronger export and the delivered stronger export were the same act instead of a local file drop that later wandered out-of-band?**

See also:
- ADR: `adrs/ADR-0106-packet-capture-strong-export-transport-boundary.md`
- packet-capture export proof-chain boundary: `docs/514-packet-capture-export-proof-chain-and-profile-posture-boundary.md`
- packet-capture stronger export approval evidence boundary: `docs/515-packet-capture-strong-export-approval-evidence-boundary.md`
- policy-constrained transports: `docs/255-policy-constrained-transports.md`
- packet-capture export transport receipt profile: `spec/packet.capture.export.transport.receipt.profile.schema.json`
- packet-capture export receipt profile: `spec/packet.capture.export.receipt.profile.schema.json`

## Why this needs a hard decision

The archive already says stronger packet export must be proof-bound and explicitly approved:

- packet capture is summary-first by default,
- stronger imports must safe-open and normalize,
- stronger normalized export stays a distinct class,
- the export receipt must join back to the session / summary / import / redaction chain,
- and the stronger export must carry explicit non-`auto` approval evidence.

But one practical ambiguity remained expensive:

- the archive could still treat a local file write as the completed stronger export,
- the actual cross-boundary delivery could then happen later through scripts, copied files, or human protocol,
- and the transport story would be reconstructed from logs or folklore after the fact.

That is too weak.
A stronger raw-byte export needs a typed answer to **how the approved stronger act actually left**.

## Accepted boundary

Across all profiles:

- `packet.capture.summary` remains the ordinary export class,
- `packet.capture.normalized` remains the stronger explicit export class,
- completed stronger raw-byte export stays on the generic `transport.policy` / `transport.receipt` lane,
- and a completed stronger export may not terminate at `destination.type = file`.

This means DeriveBSD does **not** invent a packet-capture-only delivery subsystem.
Instead, it reuses the generic transport substrate and fixes one narrow extra rule:
**a completed stronger packet raw-byte export must carry transport evidence, and a local file drop is only staging, not completion.**

## Canonical typed transport receipt profile

The archive now carries `spec/packet.capture.export.transport.receipt.profile.schema.json`.
It stays a constrained profile over `transport.receipt` and fixes the minimum shape of delivery evidence that is good enough to count as a completed stronger packet export:

- `artifact.kind = packet.capture.normalized`
- `destination.recipient` is required
- `result.status = ok`
- ticketing transports require `destination.ticket_id`

That is the actual hard decision here:
**stronger packet raw-byte export does not complete when a file appears locally; it completes when transport evidence says the approved artifact reached the intended handoff lane.**
The next coherence cut after that keeps the act digest-stable as well: `transport.receipt.artifact.digest` now needs to stay on the same normalized digest named by redaction, approval, and export evidence (`docs/517-packet-capture-strong-export-digest-stability-boundary.md`).
The final closure cut after that then requires `transport.acceptance.receipt` evidence instead of stopping at merely transported (`docs/518-packet-capture-strong-export-recipient-acceptance-boundary.md`).

## Export-receipt join rule

The packet-capture export receipt profile now requires `transport_receipt_digest` when `artifact.kind = packet.capture.normalized`.
It also rejects `destination.type = file` for that stronger class.

The chain for a completed stronger normalized export is now:

1. bounded packet-capture session,
2. typed packet-capture summary,
3. safe-open import receipt when stronger foreign artifacts were involved,
4. deterministic redaction receipt proving `packet-records-only`,
5. explicit consent receipt proving a real actor approved the stronger export,
6. transport receipt proving the approved artifact actually left through a policy-bound handoff lane,
7. transport acceptance receipt proving the recipient-side lane accepted the same artifact,
8. export receipt proving the final stronger export and naming the joined evidence.

## Product-shape meaning without a new knob

This decision intentionally reuses existing profile vocabulary.
It does not add a packet-specific profile key.

| Profile | Ordinary packet-capture export | Stronger normalized raw-byte delivery posture |
|---|---|---|
| **A fleet_host** | brokered summary-first export | ticketed/OOB-capable stronger delivery with typed transport evidence |
| **B workstation** | trusted-UI-visible summary-first export | recipient-visible stronger delivery; a local file save is staging, not completed external export |
| **C general_os** | Derive-managed summary-first export preferred | explicit stronger delivery with transport evidence even when compatibility adapters exist |
| **D appliance_factory** | minimal/redacted summary-first export | strongest delivery posture remains policy-bound, explicit, and audit-ready rather than “copied somewhere later” |

So A–D stay coherent without forking:
packet capture does not get a new transport family; it inherits the generic transport substrate and the already-decided export posture.

## Review guidance

When reviewing stronger packet-capture export changes, ask:

1. Is `packet.capture.summary` still the ordinary export path?
2. If `packet.capture.normalized` is exported, does the export receipt require `transport_receipt_digest`?
3. Does the stronger export reject `destination.type = file` as a completed handoff?
4. Does the matching transport evidence bind `artifact.kind = packet.capture.normalized`, a concrete recipient, and a successful result?
5. Is final stronger handoff still kept separate from transport success, with recipient acceptance handled by `docs/518-packet-capture-strong-export-recipient-acceptance-boundary.md`?
5. Does the target product shape still keep the transport posture it claims under pressure rather than quietly turning stronger packet export into “saved a file somewhere” adapter folklore?

## Why this is worth locking now

This is not a new transport engine.
It is a small coherence cut that turns the next fuzzy edge of stronger packet export into an implementable contract:

- A keeps stronger packet delivery case-bound and auditable,
- B keeps stronger sharing recipient-visible instead of collapsing into a background save/upload story,
- C keeps compatibility explicit instead of ambient,
- D keeps factory/regulatory packet export compatible with explicit, audit-ready handoff.

That is enough practical progress for this iteration.

Last updated: 2026-03-09r247
