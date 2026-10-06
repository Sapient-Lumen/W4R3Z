# Packet-capture stronger export approval evidence boundary

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate  

`docs/514-packet-capture-export-proof-chain-and-profile-posture-boundary.md` already fixed the proof chain for stronger packet-capture raw-byte export.
This doc fixes the next operator-facing gap:
**what proves that stronger packet raw-byte export was actually approved by a real actor instead of quietly riding an ambient export path?**

See also:
- ADR: `adrs/ADR-0105-packet-capture-strong-export-approval-evidence-boundary.md`
- packet-capture export proof-chain boundary: `docs/514-packet-capture-export-proof-chain-and-profile-posture-boundary.md`
- consent UX contract: `docs/256-consent-ux-contract.md`
- high-risk approval posture by profile: `docs/474-high-risk-approval-posture-by-profile.md`
- packet-capture export consent request profile: `spec/packet.capture.export.consent.request.profile.schema.json`
- packet-capture export consent receipt profile: `spec/packet.capture.export.consent.receipt.profile.schema.json`
- stronger export transport boundary: `docs/516-packet-capture-strong-export-transport-boundary.md`
- stronger export recipient-acceptance boundary: `docs/518-packet-capture-strong-export-recipient-acceptance-boundary.md`
- stronger export destination-bound approval boundary: `docs/519-packet-capture-strong-export-destination-bound-approval-boundary.md`

## Why this needs a hard decision

The archive already says stronger packet export must be proof-bound:

- packet capture is summary-first by default,
- stronger imported captures must safe-open and normalize,
- normalized raw-byte export stays a stronger explicit class,
- and the export receipt must join back to the session / summary / import / redaction chain.

But one practical ambiguity remained expensive:

- a stronger normalized packet export could still flow through a generic export path,
- the receipt could prove where the bytes came from,
- yet the approval story could still be "the system auto-did it under some policy".

That is too weak.
A stronger raw-byte export needs a typed answer to **who approved this stronger act**.

## Accepted boundary

Across all profiles:

- `packet.capture.summary` remains the ordinary export class,
- `packet.capture.normalized` remains the stronger explicit export class,
- stronger raw-byte export stays on the generic `consent.request` / `consent.receipt` lane,
- and that stronger lane must carry explicit approval evidence that is not `auto`.

This means DeriveBSD does **not** invent a packet-capture-only approval subsystem.
Instead, it reuses the generic consent substrate and fixes one narrow extra rule:
**stronger packet raw-byte export may be GUI-approved, TTY-approved, or OOB-approved, but not auto-approved.**

## Canonical typed approval request profile

The archive now carries `spec/packet.capture.export.consent.request.profile.schema.json`.
It stays a constrained profile over `consent.request` and fixes the minimum inputs for a stronger packet export approval request:

- `action.kind = export`
- `action.policy_digest`
- `action.artifact_digest`
- `action.lease_id`
- `secure_attention_required = true`

This keeps the approval request explicit about what stronger artifact is leaving, under which policy, and under which lease-derived authority. Later archive cuts tighten that further in two directions: `consent.request.action.artifact_digest` is expected to stay on the same bytes later named by transport and export evidence (`docs/517-packet-capture-strong-export-digest-stability-boundary.md`), and the stronger approval request is now destination-bound too so `action.destination` stays aligned with the later transport / recipient-acceptance / export destination tuple (`docs/519-packet-capture-strong-export-destination-bound-approval-boundary.md`).

## Canonical typed approval receipt profile

The archive now carries `spec/packet.capture.export.consent.receipt.profile.schema.json`.
It stays a constrained profile over `consent.receipt` and fixes the minimum shape of approval evidence that is good enough to authorize a stronger packet export:

- `outcome = approved`
- `method ∈ { gui, tty, oob }`
- `method = auto` is out of bounds

That is the actual hard decision here:
**stronger packet raw-byte export cannot hide behind automatic approval even when the underlying export path is otherwise automated.**

## Export-receipt join rule

The packet-capture export receipt profile now requires `consent_receipt_digest` when `artifact.kind = packet.capture.normalized`.
That makes the approval evidence a first-class part of the stronger export chain instead of an optional hint.
The later closure step is now explicit too: approval still is not the end of the act, because final stronger export also needs recipient acceptance evidence (`docs/518-packet-capture-strong-export-recipient-acceptance-boundary.md`).

The chain for a stronger normalized export is now:

1. bounded packet-capture session,
2. typed packet-capture summary,
3. safe-open import receipt when stronger foreign artifacts were involved,
4. deterministic redaction receipt proving `packet-records-only`,
5. explicit consent receipt proving a real actor approved the stronger export,
6. transport receipt proving the approved artifact actually left through the intended handoff lane,
7. export receipt proving the completed stronger export under policy,
8. a digest-stable chain proving those receipts still talk about the same bytes (`docs/517-packet-capture-strong-export-digest-stability-boundary.md`),
9. and recipient-acceptance evidence proving the recipient-side lane actually accepted the same artifact (`docs/518-packet-capture-strong-export-recipient-acceptance-boundary.md`).

## Product-shape meaning without a new knob

This decision intentionally reuses existing profile vocabulary.
It does not add a packet-specific profile key.

| Profile | Ordinary packet-capture export | Stronger normalized raw-byte export approval posture |
|---|---|---|
| **A fleet_host** | brokered summary-first export | brokered stronger action with explicit TTY/OOB or equivalent approval evidence |
| **B workstation** | trusted-UI-visible summary-first export | trusted-UI-visible stronger action with explicit human approval evidence |
| **C general_os** | Derive-managed summary-first export preferred | explicit stronger action with real approval evidence even when compatibility adapters exist |
| **D appliance_factory** | minimal/redacted summary-first export | strongest approval lane remains explicit and offline/OOB-capable rather than ambient |

So A–D stay coherent without forking:
packet capture does not get a new approval family; it inherits the generic consent substrate and the already-decided high-risk approval posture.

## Review guidance

When reviewing stronger packet-capture export changes, ask:

1. Is `packet.capture.summary` still the ordinary export path?
2. If `packet.capture.normalized` is exported, does the export receipt require `consent_receipt_digest`?
3. Does the matching consent request bind the export `policy_digest`, `artifact_digest`, and `lease_id`?
4. Does the matching stronger approval request also bind `action.destination` when normalized raw bytes are leaving?
5. Does the matching approval evidence avoid `method = auto`?
6. Does the target product shape still keep the approval posture it claims under pressure rather than silently turning stronger packet export into a background adapter action?

## Why this is worth locking now

This is not a new workflow engine.
It is a small coherence cut that turns the last fuzzy edge of stronger packet export into an implementable contract:

- A keeps brokered packet export explainable,
- B keeps stronger sharing visibly human-approved,
- C keeps compatibility explicit instead of ambient,
- D keeps factory/regulatory packet export compatible with offline/OOB review.

That is enough practical progress for this iteration.

Last updated: 2026-03-09r248
