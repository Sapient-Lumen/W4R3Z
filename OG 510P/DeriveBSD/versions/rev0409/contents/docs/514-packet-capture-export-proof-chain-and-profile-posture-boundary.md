# Packet-capture export proof-chain and compiled profile posture boundary

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Plan→Apply→Receipt  

`docs/507-packet-capture-session-and-summary-first-export-boundary.md` already made packet capture summary-first.
`docs/511-packet-capture-strong-artifact-safe-open-intake-and-normalize-boundary.md` and `docs/512-packet-capture-normalization-redaction-receipt-boundary.md` then fixed the safe-open + normalization path for stronger packet artifacts.
`docs/513-packet-capture-evidence-joins-in-incident-bundles-boundary.md` kept support bundles on typed digest joins rather than default raw packet members.
This doc fixes the next practical export gap:
**if normalized raw packet bytes actually leave the system, what keeps that stronger act proof-bound instead of collapsing back into `.pcapng` folklore?**

See also:
- ADR: `adrs/ADR-0104-packet-capture-export-proof-chain-and-profile-posture.md`
- export portal / policies: `docs/251-export-policies-and-support-bundle-portal.md`
- export boundary posture by profile: `docs/466-export-boundary-posture-by-profile.md`
- packet-capture normalization proof boundary: `docs/512-packet-capture-normalization-redaction-receipt-boundary.md`
- packet-capture incident-bundle joins: `docs/513-packet-capture-evidence-joins-in-incident-bundles-boundary.md`
- packet-capture export policy profile: `spec/packet.capture.export.policy.profile.schema.json`
- packet-capture export receipt profile: `spec/packet.capture.export.receipt.profile.schema.json`
- stronger export approval evidence boundary: `docs/515-packet-capture-strong-export-approval-evidence-boundary.md`
- stronger export transport boundary: `docs/516-packet-capture-strong-export-transport-boundary.md`
- stronger export recipient-acceptance boundary: `docs/518-packet-capture-strong-export-recipient-acceptance-boundary.md`
- packet-capture export transport receipt profile: `spec/packet.capture.export.transport.receipt.profile.schema.json`
- packet-capture export transport acceptance receipt profile: `spec/packet.capture.export.transport.acceptance.receipt.profile.schema.json`

## Why this needs a hard decision

The archive already says three important true things:

- packet capture is a stronger authority lane,
- `packet.capture.summary` is the ordinary review/export surface,
- and stronger sideband/decryption-bearing captures must safe-open, normalize, and prove that normalization with deterministic redaction evidence.

But one practical ambiguity remained expensive:

- support bundles no longer smuggle raw packet bytes by default,
- yet a support/export workflow could still quietly standardize on “upload the normalized `.pcapng`”,
- and the ordinary `export.receipt` would only say that some bytes left under some policy.

That is not enough if DeriveBSD wants packet-capture export to stay explainable.
When a stronger normalized raw-byte export happens, reviewers need the proof chain that explains **why this stronger act was allowed at all**.

## Accepted boundary

Across all profiles:

- `packet.capture.summary` remains the **ordinary** export class,
- normalized raw packet bytes remain a **stronger explicit** export class,
- both still use the generic `export.policy` / `export.receipt` lane,
- and stronger normalized exports must carry typed supporting evidence that joins them back to the session/summary/import/redaction chain.

This means DeriveBSD does **not** add a new `product.profiles` key for packet capture.
Instead, packet-capture export posture is a **compiled consequence** of the existing `evidence`, `evidence_exports`, and packet-capture boundaries.

## Canonical typed policy profile

The archive now carries `spec/packet.capture.export.policy.profile.schema.json`.
It stays a constrained profile over the generic `export.policy` kind and fixes two ordinary/stronger classes:

- `packet.capture.summary`
- `packet.capture.normalized`

The policy profile requires:

- a `packet.capture.summary` rule with `allow_raw_blobs = false`,
- a distinct `packet.capture.normalized` rule when normalized raw bytes may leave the system,
- and for that stronger rule, an explicit `redaction_transform_digest` plus `allow_raw_blobs = true`.

This keeps the policy question narrow:
summary export is routine,
normalized raw-byte export is explicit.

## Canonical typed receipt profile

The archive now carries `spec/packet.capture.export.receipt.profile.schema.json`.
It stays a constrained profile over the generic `export.receipt` kind and uses the new generic `supporting_evidence[]` join surface.

For `artifact.kind = packet.capture.summary`, the packet-capture receipt profile requires at least the bounded session join.

For `artifact.kind = packet.capture.normalized`, the receipt profile requires supporting evidence roles for:

- `session`
- `summary`
- `import-receipt`
- `redaction-receipt`

The next archive cut also makes the approval edge explicit rather than optional: stronger packet raw-byte export now requires `consent_receipt_digest`, and the matching stronger export approval evidence must come from the generic consent lane with a non-`auto` method (`docs/515-packet-capture-strong-export-approval-evidence-boundary.md`).
The next cut after that fixes execution as well: stronger packet raw-byte export now also requires `transport_receipt_digest`, and `destination.type = file` no longer counts as a completed stronger handoff (`docs/516-packet-capture-strong-export-transport-boundary.md`).
The next cut after that fixes byte identity as well: stronger packet raw-byte export is now digest-stable, so approval / transport / export receipts must keep the same normalized digest instead of drifting across related derivatives (`docs/517-packet-capture-strong-export-digest-stability-boundary.md`).
The next cut after that fixes closure as well: final stronger export now also requires `transport_acceptance_receipt_digest` plus `delivery_state = recipient-accepted`, so the chain stops at recipient acceptance rather than merely transported (`docs/518-packet-capture-strong-export-recipient-acceptance-boundary.md`). The stronger closure cut after that then requires `acceptance.remote_artifact_digest` so recipient acceptance confirms the same normalized bytes rather than merely a plausible remote object (`docs/520-packet-capture-strong-export-recipient-digest-confirmation-boundary.md`).

That is the actual hard decision here:
**a stronger packet-capture raw-byte export must carry the proof chain that explains why the bytes are no longer just “some safer-looking file”.**

## Product-shape meaning without a new knob

This decision intentionally reuses the existing profile surfaces rather than growing packet-specific profile vocabulary.

| Profile | Ordinary packet-capture export | Stronger normalized raw-byte export |
|---|---|---|
| **A fleet_host** | brokered summary-first export | brokered stronger action with proof-bound receipt |
| **B workstation** | trusted-UI-visible summary-first export | trusted-UI-visible stronger action with proof-bound receipt |
| **C general_os** | Derive-managed summary-first export preferred | explicit adapter/compatibility use allowed only as a stronger proof-bound action |
| **D appliance_factory** | minimal/redacted summary-first export | strongest approval/transparency posture still applies to the proof-bound stronger action |

So A–D stay coherent without forking:
packet capture does not get its own product family; it inherits the already-decided export posture.

## Review guidance

When reviewing packet-capture export changes, ask:

1. Is `packet.capture.summary` still the ordinary export surface?
2. If normalized raw bytes are allowed out, is that expressed as a distinct stronger `packet.capture.normalized` policy rule rather than a quiet extension of summary export?
3. Does the export receipt carry typed `supporting_evidence` joins back to the session/summary/import/redaction proof chain?
4. For `packet.capture.normalized`, does the stronger export also require `consent_receipt_digest` rather than relying on an ambient or automatic path?
5. For final stronger export, does the receipt also require `transport_acceptance_receipt_digest` and `delivery_state = recipient-accepted` rather than stopping at send success?
5. Does the target profile keep the posture it claims under pressure, rather than letting packet exports become a quiet fork of the support story?
6. Are support bundles still digest-first while stronger raw-byte export remains a separate explicit act?

## Why this is worth locking now

This is not a new export subsystem.
It is a small coherence cut that makes the current packet-capture decisions implementable all the way to the external handoff edge:

- A keeps oncall packet export brokered and explainable,
- B keeps stronger packet sharing visible to the human,
- C keeps compatibility explicit instead of ambient,
- D keeps the factory/regulatory story proof-bound and auditable.

That is enough progress for this iteration.

Last updated: 2026-03-09r249