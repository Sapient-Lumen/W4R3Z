# Export policies + support-bundle portal

DeriveBSD already has **incident/support bundles** (`docs/216-incident-snapshots-and-support-bundles.md`) and **deterministic redaction transforms** (`docs/195-deterministic-redaction-transforms.md`).

The missing groundfloor feature is: **a first-class, user-/policy-mediated export path**.

Older ecosystems often treat "collect diagnostics" as one tool, and "send it to someone" as an ad-hoc follow-up (scp the tarball, paste logs, attach it to a ticket). That breaks least-authority and makes it hard to prove what was shared.

This doc introduces:
- `export.policy`: a *share contract* (what may be exported, to whom, and with what transforms)
- `export.receipt`: evidence that an export occurred (with policy + transforms + recipients)
- a **Support Bundle Export Portal**: a portal-shaped UI/UX that binds consent + routing to the policy surface
- `transport.policy` + `transport.receipt`: transport adapters as a policy-bound lane (`docs/255-policy-constrained-transports.md`).
- `consent.request` + `consent.receipt`: a uniform approval/consent contract across GUI/TTY/OOB (`docs/256-consent-ux-contract.md`).
- `export.transparency.entry`: optional append-only logging of export events (`docs/254-export-transparency-logs.md`).
- packet-capture session/export contract (`docs/507-packet-capture-session-and-summary-first-export-boundary.md`).

## Goals

- Make every export **reviewable** (policy as data) and **auditable** (receipt as evidence).
- Keep exports **least-authority**: exporting is not equivalent to "root can read everything".
- Make bundle sharing **reproducible**: two parties can verify they are looking at the same exported bytes.
- Integrate cleanly with existing lanes:
  - incident bundles
  - tracing outputs
  - crash artifacts
  - redaction transforms
  - leases and breakglass

## Non-goals

- This does *not* define a specific transport (email, upload, pastebin, ticket system). The export path is a **pluggable adapter**, constrained by `transport.policy` (`docs/255-policy-constrained-transports.md`).
- This does *not* require a GUI. The portal model can be implemented as:
  - GUI prompt
  - TTY prompt with secure attention
  - OOB approval flow

## Prior art to steal

- **XDG Desktop Portal** model: sandboxed apps request a mediated capability and get a handle (not raw filesystem access). The FileChooser and FileTransfer portals are concrete examples of "user-mediated export" in practice.
  - FileChooser: https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.FileChooser.html
  - FileTransfer: https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.FileTransfer.html
- **sosreport** operational lesson: collect a standard bundle for support, but treat it as sensitive; shipping it is a distinct action.
  - RHEL sos report docs: https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/8/html-single/generating_sos_reports_for_technical_support/index

## Key idea

In DeriveBSD, "export" is a **separately authorized step**:

1. A bundle exists (or is produced) as a content-addressed artifact.
2. A policy allows exporting *this class of artifact* to *this class of recipient*.
3. A lease authorizes this export attempt (portal grant or breakglass grant).
4. The export runs through an adapter and produces an `export.receipt`.

## Artifact boundaries

### `export.policy` (new)

A policy object that declares:
- allowed artifact kinds (incident bundles, trace outputs, crash reports, …)
- mandatory transforms (redaction transform digests, field drops)
- destination constraints (recipient identities, ticket ids, allowed transports)
- whether **interactive consent** is required (portal)
- whether **two-person approval** is required
- encryption requirements (age/PGP/CMS)

See: `spec/export.policy.schema.json`.

### `export.receipt` (new)

Evidence that an export occurred, including:
- exported artifact digest(s)
- policy digest
- redaction transform digest (if applied)
- lease id used to authorize the export (if any)
- transport adapter metadata (destination, upload id, ticket id)

See: `spec/export.receipt.schema.json`.


## Related evidence objects (optional but recommended)

Exports often cross trust boundaries. For high-assurance deployments, prefer emitting:
- `consent.receipt` (who approved the export, and how)
- `transport.receipt` (where the bytes went, metadata-only)
- `export.transparency.entry` (append-only log record + inclusion proof)

These digests may be embedded into `export.receipt` and referenced from incident bundles.

Schemas:
- `spec/consent.receipt.schema.json`
- `spec/transport.receipt.schema.json`
- `spec/export.transparency.entry.schema.json`

## Support Bundle Export Portal (concept)

A portal call takes:
- `bundle_digest` (incident bundle payload digest or a logical bundle id)
- `export_policy_digest`
- `recipient` (or recipient class) + `ticket_id`
- optional `requested_transform_digest` (must be permitted by policy)

It returns:
- a **timeboxed lease** authorizing the export attempt
- a **receipt digest/id** after completion

This mirrors portal ergonomics: request capability → get scoped handle → perform action.

## How this composes with breakglass

Breakglass grants already include `export-support-bundle` as an allowed op.
In DeriveBSD, breakglass does *not* bypass export policy:
- breakglass may enable the *portal path* (or a CLI path) to be used in recovery mode
- export still produces an `export.receipt`
- export policy still defines transforms and destination constraints

## Product-shape default

The default export boundary is now fixed in `docs/466-export-boundary-posture-by-profile.md`.
That means:

- A keeps export brokered/ticketed/encrypted rather than oncall shell folklore.
- B keeps user-visible recipient + redaction posture in the trusted UI rather than background upload helpers.
- C prefers Derive-managed export lanes but allows explicit adapter fallback.
- D keeps factory/regulatory export minimal, redacted, strongly approved, and transparency-aware by default.

## Metadata preservation boundary

If an export is expected to preserve origin/quarantine context across a lossy filesystem, archive tool, or foreign transport, it must use an official portal/bundle lane that can preserve or rehydrate labels from authoritative `content.origin` records.

If policy intentionally clears metadata, that is acceptable only when explicit in policy/transform choice and still receipted as such. Raw compatibility exports that drop labels are outside the guaranteed provenance-preserving lane.

## Operational guidance

- Default export policy for external vendors should:
  - forbid raw core/kernel dumps
  - forbid raw packet payload export by default
  - require redaction transforms
  - require encryption
  - require ticket id
- For packet capture, prefer exporting `packet.capture.session` metadata, typed `packet.capture.selector` intent, and `packet.capture.summary` first; shipping raw packet bytes should remain an explicit stronger exception rather than the default support workflow.
- Treat `sideband-metadata-present` and especially `decryption-material-present` raw capture artifacts as a stronger lane still: they do not belong on the normal support/export path just because the underlying file format permits them.
- The official stronger lane is the typed safe-open packet-capture import lane (`spec/content.import.packet-capture.plan.schema.json`, `spec/content.import.packet-capture.receipt.schema.json`): keep the original artifact quarantined, and only promote/export a normalized `packet-records-only` derivative or `packet.capture.summary` through ordinary support flows.
- For normalized packet-capture derivatives, require deterministic redaction evidence as well: the import receipt should point at a packet-capture `redaction-transform` + `redaction-receipt`, and ordinary raw-byte export should stay `summary-only` unless that proof ends at `ordinary-review-export-eligible` with `output_metadata_posture = packet-records-only` (`docs/512-packet-capture-normalization-redaction-receipt-boundary.md`).
- Stronger packet-capture raw-byte export should use the typed packet-capture export profiles: `packet.capture.summary` remains the ordinary export class, `packet.capture.normalized` remains the stronger explicit class, and the matching packet-capture export receipt profile should carry `supporting_evidence` joins back to the session / summary / import-receipt / redaction-receipt chain (`spec/packet.capture.export.policy.profile.schema.json`, `spec/packet.capture.export.receipt.profile.schema.json`, `docs/514-packet-capture-export-proof-chain-and-profile-posture-boundary.md`).
- Stronger `packet.capture.normalized` export must also bind to the generic consent lane through the typed packet-capture export consent profiles: the request binds policy/artifact/lease state **plus** `action.destination`, the completed stronger export carries `consent_receipt_digest`, and the approval evidence may be GUI/TTY/OOB but not `method = auto` (`spec/packet.capture.export.consent.request.profile.schema.json`, `spec/packet.capture.export.consent.receipt.profile.schema.json`, `docs/515-packet-capture-strong-export-approval-evidence-boundary.md`, `docs/519-packet-capture-strong-export-destination-bound-approval-boundary.md`).
- Completed stronger `packet.capture.normalized` export must also stay transport-bound: the packet-capture export receipt profile now requires `transport_receipt_digest`, rejects `destination.type = file`, and uses a constrained packet-capture transport receipt profile so a local file save is only staging, not the completed stronger handoff (`spec/packet.capture.export.transport.receipt.profile.schema.json`, `docs/516-packet-capture-strong-export-transport-boundary.md`).
- Stronger `packet.capture.normalized` export must also stay digest-stable across the whole stronger act: `redaction-receipt`.output, `consent.request.action.artifact_digest`, `transport.receipt.artifact.digest`, `transport.acceptance.receipt.artifact.digest`, and `export.receipt.artifact.digest` must keep the same normalized digest instead of letting “approved one file, sent another” folklore creep back in (`docs/517-packet-capture-strong-export-digest-stability-boundary.md`).
- Final stronger `packet.capture.normalized` export now also needs recipient-side closure evidence: `delivery_state = recipient-accepted` plus `transport_acceptance_receipt_digest`, joined through `transport.acceptance.receipt`, so transport success no longer counts as the final stronger handoff by itself (`spec/transport.acceptance.receipt.schema.json`, `spec/packet.capture.export.transport.acceptance.receipt.profile.schema.json`, `docs/518-packet-capture-strong-export-recipient-acceptance-boundary.md`).
- That recipient-side closure is now remote-digest-confirming too: `acceptance.remote_artifact_digest` must echo the same normalized digest rather than merely point at a plausible attachment reference (`docs/520-packet-capture-strong-export-recipient-digest-confirmation-boundary.md`).
- That stronger closure is now remote-object-continuous too: `transport.receipt.result.remote_id`, `transport.acceptance.receipt.acceptance.remote_reference`, and `export.receipt.adapter.remote_id` must stay on the same remote object identifier instead of letting “some object in the same case” stand in for the accepted artifact (`docs/521-packet-capture-strong-export-remote-object-continuity-boundary.md`).
- That stronger closure is now remote-validator-continuous too: `transport.receipt.result.remote_validator`, `transport.acceptance.receipt.acceptance.remote_validator`, and `export.receipt.adapter.remote_validator` must stay on the same remote validator instead of collapsing the stronger proof chain back to object id alone (`docs/522-packet-capture-strong-export-remote-validator-continuity-boundary.md`).
- That stronger closure is now remote-protection-shaped too: `transport.acceptance.receipt.acceptance.remote_protection` and `export.receipt.adapter.remote_protection` must stay on the same remote protection posture so stronger packet handoff no longer calls a transient remote copy “durable evidence” without saying what overwrite/delete resistance the recipient-side lane claimed (`docs/523-packet-capture-strong-export-remote-protection-posture-boundary.md`).
- That stronger closure is now remote-locator-continuous too: `transport.receipt.result.remote_locator`, `transport.acceptance.receipt.acceptance.remote_locator`, and `export.receipt.adapter.remote_locator` must stay on the same remote locator so later evidence retrieval does not collapse back into portal folklore and manual ticket clicking (`docs/524-packet-capture-strong-export-remote-locator-continuity-boundary.md`).
- Later stronger packet evidence re-check should now use `transport.reverification.receipt` as a typed follow-up lane: keep `reverification.body_downloaded = false` and preserve the same accepted remote validator / protection posture / locator instead of re-downloading packet bytes or trusting screenshots (`spec/transport.reverification.receipt.schema.json`, `spec/packet.capture.export.transport.reverification.receipt.profile.schema.json`, `docs/525-packet-capture-strong-export-remote-reverification-boundary.md`).
- That stronger approval is now recipient-bound as well as byte-bound: `consent.request.action.destination`, `transport.receipt.destination`, `transport.acceptance.receipt.recipient`, and `export.receipt.destination` must keep the same approved destination tuple instead of letting ticket or recipient drift hide behind an otherwise valid proof chain (`docs/519-packet-capture-strong-export-destination-bound-approval-boundary.md`).
- Official support bundles should carry packet-capture session/summary/import/redaction receipt digests rather than raw packet payloads by default; if raw bytes actually leave the system, that remains a separate stronger export action rather than ordinary bundle membership (`docs/513-packet-capture-evidence-joins-in-incident-bundles-boundary.md`).
- Provide a `bundle-min` mode (see `docs/246…` + `docs/253…`) so exports are small and explainable.

Last updated: 2026-03-09r254