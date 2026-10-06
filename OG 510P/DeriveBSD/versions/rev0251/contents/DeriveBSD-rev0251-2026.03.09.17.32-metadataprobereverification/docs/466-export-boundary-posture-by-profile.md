# Export boundary posture by profile

**Tier:** C (Optional lane)  
**Profiles:** A, B, C, D  
**Pillars:** operability, isolation, supply-chain  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate  

DeriveBSD already has an export-policy lane.
What this doc decides is narrower and more important for coherence:
**what is the default posture for evidence leaving the system in each product shape?**

This is intentionally **not** a transport-backend or ticket-system doc.
It is a product-default decision.

See also:
- ADR: `adrs/ADR-0056-export-boundary-posture-by-profile.md`
- export portal / policies: `docs/251-export-policies-and-support-bundle-portal.md`
- export drift review surface: `docs/433-export-policy-diff-as-review-surface.md`
- deterministic redaction: `docs/195-deterministic-redaction-transforms.md`
- product profiles: `docs/411-product-profiles-as-compilation-target.md`

## Why this needs a hard decision

Support bundles, traces, crash artifacts, and receipts are only safe if **export** stays a first-class boundary.
Otherwise every mature system eventually rediscovers the same failure mode:

- collection is standardized,
- shipping is not,
- and under incident pressure people email tarballs, relax approvals, or enable raw uploads "just for now."

If DeriveBSD leaves this as implementation folklore, A–D drift toward incompatible defaults:

- fleet exports become oncall improvisation,
- workstation support prompts become unclear about who receives what,
- general-OS compatibility silently turns into ambient adapters,
- and factory/regulatory evidence handoff becomes impossible to audit.

So we fix the **default export authority + redaction + approval posture** now while leaving transport backends, exact redaction catalogs, and transparency metadata shape open.

## Product-shape defaults

| Profile | `evidence_exports` default | Practical meaning |
|---|---|---|
| A (`fleet_host`) | `brokered-ticketed-encrypted-external-two-person` | Evidence export is brokered and ticket-shaped; external handoff is encrypted; boundary expansion normally requires stronger review. |
| B (`workstation`) | `user-mediated-redacted-recipient-visible-encrypted-external` | The user sees recipient + redaction posture in a trusted-UI flow; external export is encrypted and remembered authority must still land in leases/policy. |
| C (`general_os`) | `brokered-preferred-ticketed-explicit-adapter-fallback` | Derive-managed export lanes are preferred, but explicit compatibility adapters remain possible rather than pretending all ecosystems vanish. |
| D (`appliance_factory`) | `minimal-redacted-encrypted-two-person-transparency-required` | Export stays minimal/redacted by default; external sharing is encrypted, strongly approved, and transparency-backed in the high-assurance lane. |

These values live in `spec/examples/product.profiles.json` and are guarded by `tools/check_product_profiles.py`.

## Cross-profile invariants

Regardless of profile:

- export is a separately governed lane, not a follow-up side effect of collection
- recipient class/identity, transform, and transport remain explicit and receipted
- raw blob export is exceptional rather than ambient
- external recipients should not receive unencrypted Derive-managed exports by default
- remembered export authority must land in a lease or durable policy object

## What this fixes by profile

### A) Secure fleet host (`fleet_host`)

Default: `brokered-ticketed-encrypted-external-two-person`

- Fleet support/export remains operator-initiated and brokered rather than host-local improvisation.
- External recipients should be case/ticket-bound and encrypted by default.
- High-risk export posture changes belong in review/gate lanes, not ad-hoc incident shell history.

### B) Secure workstation (`workstation`)

Default: `user-mediated-redacted-recipient-visible-encrypted-external`

- The human can choose to share evidence, but the trusted UI must make the recipient and redaction posture visible.
- External export should default to encrypted handoff.
- Remembered support/export permissions remain leased or policy-shaped; the workstation should not grow an ambient background support uploader.

### C) General-purpose OS (`general_os`)

Default: `brokered-preferred-ticketed-explicit-adapter-fallback`

- Broad compatibility keeps classic support/upload tooling possible.
- The preferred path still uses Derive-managed policy + receipt lanes.
- Adapter fallback must stay explicit and killable rather than silently becoming the real product default.

### D) Appliance factory / regulatory (`appliance_factory`)

Default: `minimal-redacted-encrypted-two-person-transparency-required`

- Factory/regulatory exports should prefer minimal, redacted evidence bundles by default.
- Cross-boundary sharing should be strongly approved, encrypted, and transparently logged.
- Production evidence sharing should not drift into invisible convenience export or raw blob folklore.

## Packet-capture compiled consequence

This export posture also constrains packet capture without growing a new profile key.
That is a deliberate **compiled consequence** of the existing export boundary:

- `packet.capture.summary` is the ordinary packet-capture export class across A–D,
- `packet.capture.normalized` is the stronger explicit raw-byte class,
- stronger `packet.capture.normalized` export also stays explicit at the approval edge: it carries `consent_receipt_digest`, reuses the generic consent lane, and does not allow `method = auto` to stand in for real approval (`docs/515-packet-capture-strong-export-approval-evidence-boundary.md`),
- completed stronger `packet.capture.normalized` export also stays transport-bound: it carries `transport_receipt_digest`, uses the generic transport lane, and does not allow `destination.type = file` to count as completed handoff (`docs/516-packet-capture-strong-export-transport-boundary.md`),
- stronger `packet.capture.normalized` export is also digest-stable: approval, transport, transport acceptance, and export receipts must keep the same normalized digest rather than silently mutating the artifact mid-flight (`docs/517-packet-capture-strong-export-digest-stability-boundary.md`),
- stronger `packet.capture.normalized` export is also now closure-bound: final stronger handoff is `recipient-accepted`, so the stronger export receipt carries a transport acceptance receipt rather than stopping at “transport probably worked” (`docs/518-packet-capture-strong-export-recipient-acceptance-boundary.md`),
- stronger `packet.capture.normalized` recipient acceptance is also now remote-digest-confirming, so `acceptance.remote_artifact_digest` must stay on the same normalized digest rather than merely pointing at a plausible remote attachment (`docs/520-packet-capture-strong-export-recipient-digest-confirmation-boundary.md`),
- stronger `packet.capture.normalized` export is also remote-object-continuous: `transport.receipt.result.remote_id`, `transport.acceptance.receipt.acceptance.remote_reference`, and `export.receipt.adapter.remote_id` must stay on the same remote object identifier rather than silently drifting across multiple portal objects in one case (`docs/521-packet-capture-strong-export-remote-object-continuity-boundary.md`),
- stronger `packet.capture.normalized` export is also remote-validator-continuous: `transport.receipt.result.remote_validator`, `transport.acceptance.receipt.acceptance.remote_validator`, and `export.receipt.adapter.remote_validator` must stay on the same remote validator rather than silently collapsing back to object id alone (`docs/522-packet-capture-strong-export-remote-validator-continuity-boundary.md`),
- stronger `packet.capture.normalized` export is also remote-protection-shaped: `transport.acceptance.receipt.acceptance.remote_protection` and `export.receipt.adapter.remote_protection` must stay on the same remote protection posture rather than silently turning a transient recipient copy into “durable evidence” folklore (`docs/523-packet-capture-strong-export-remote-protection-posture-boundary.md`),
- stronger `packet.capture.normalized` export is also remote-locator-continuous: `transport.receipt.result.remote_locator`, `transport.acceptance.receipt.acceptance.remote_locator`, and `export.receipt.adapter.remote_locator` must stay on the same remote locator rather than leaving later evidence lookup to portal folklore (`docs/524-packet-capture-strong-export-remote-locator-continuity-boundary.md`),
- later remote reverification is also metadata-first: `transport.reverification.receipt` can re-check the accepted remote packet object, but canonical stronger follow-up keeps `reverification.body_downloaded = false` and preserves the same accepted remote validator / protection posture / locator instead of relying on screenshots or another raw-byte download (`docs/525-packet-capture-strong-export-remote-reverification-boundary.md`),
- stronger `packet.capture.normalized` export is also destination-bound: approval, transport, recipient acceptance, and export must keep the same approved destination tuple rather than silently retargeting the same bytes to a different ticket or recipient (`docs/519-packet-capture-strong-export-destination-bound-approval-boundary.md`),
- and the approval/visibility/transparency posture for that stronger class follows the already-decided `evidence_exports` default instead of inventing a packet-only product fork.

## What this does *not* decide

Still open:

- exact `risk_flags` vocabulary for `export.policy.diff`
- which export-policy changes require two-person integrity in which profiles by default
- transport-independent ticket semantics across adapters
- exact transparency metadata shape (hashed ids/recipients, scopes, retention)
- default redaction catalogs and raw-blob exception workflows

That work stays implementation-level.
This doc only fixes the product-default boundary so the archive can keep converging without drifting.

## Design cue from current systems

Three ecosystem cues matter here:

- portalized desktops treat file transfer/export as a brokered authority rather than raw app-local filesystem reach,
- operational support tooling like `sos report` treats bundle generation as standardized but sensitive enough to warrant deliberate handling,
- and mature support systems often bind uploads to case/ticket workflows and optional cleaning/redaction rather than pretending "collect" and "ship" are the same action.

DeriveBSD should steal the lesson, not the ambient upload folklore.

Last updated: 2026-03-09r254