# Policy-constrained transports (ticketing, uploads, OOB)

`export.policy` defines *whether* you may share a class of artifacts and what transforms apply.
But export still needs to answer: **how do bytes move** (ticket systems, vendor portals, uploads, removable media)?

Older ecosystems bake transport details into ad-hoc scripts, which makes it hard to:
- review destinations (domains, tickets, recipients)
- audit what transport actually happened
- avoid leaking secrets in logs/receipts

This doc introduces transport as a **typed, policy-bound adapter lane**:
- `transport.policy`: constraints on allowed transport adapters and destinations
- `transport.receipt`: evidence of a concrete transport action (metadata only)

## Prior art to steal

Ticketing systems are the real world. Treat them as first-class transports:
- Jira “add attachment” REST patterns:
  - Cloud KB: https://support.atlassian.com/jira/kb/how-to-add-an-attachment-to-a-jira-cloud-issue-using-rest-api/
  - Data Center KB: https://support.atlassian.com/jira/kb/how-to-add-an-attachment-to-a-jira-issue-using-rest-api/
- ServiceNow Attachment API overview: https://www.servicenow.com/docs/r/api-reference/rest-apis/c_AttachmentAPI.html

## New artifacts

### `transport.policy`

A transport policy declares:
- which adapter kinds may be used (`jira`, `servicenow`, `https-upload`, `sftp`, `oob`, …)
- destination constraints (allowed domains/realms, ticket id patterns)
- size limits, TLS requirements, and other guardrails
- authentication *modes* (but never embed secrets)

See: `spec/transport.policy.schema.json`.

### `transport.receipt`

A transport receipt records:
- artifact digest + size
- which transport adapter ran
- normalized destination metadata (ticket id, recipient class, domain)
- status and remote identifiers (upload id), without secrets

See: `spec/transport.receipt.schema.json`.

## How it composes with export

- `export.policy` may reference a `transport.policy` via `transport_policy_digest`
- `export.receipt` may reference the `transport.receipt` via `transport_receipt_digest`
- export tooling should treat “transport is complete” only when the transport receipt is emitted successfully
- stronger `packet.capture.normalized` export now makes that generic rule non-optional: a completed stronger packet export must carry `transport_receipt_digest`, the transport receipt must bind `artifact.kind = packet.capture.normalized`, and `destination.type = file` no longer counts as a completed stronger handoff (`spec/packet.capture.export.transport.receipt.profile.schema.json`, `docs/516-packet-capture-strong-export-transport-boundary.md`)

This separation helps in audits:
- export policy: what we *intended* to allow
- transport policy: what destinations we *actually* permit
- transport receipt: what *happened*
- transport acceptance receipt: what the recipient-side lane accepted
- for stronger packet export, the joined transport receipt should still describe the same bytes named by approval and export evidence; for HTTP-style transports, `Content-Digest` from RFC 9530 is a good adapter-level clue, but the archive boundary remains the receipted digest chain (`docs/517-packet-capture-strong-export-digest-stability-boundary.md`).
- for stronger `packet.capture.normalized` export, final handoff is now `recipient-accepted`, not merely transported: join `transport.acceptance.receipt`, require `transport_acceptance_receipt_digest`, and keep the acceptance receipt on the same normalized digest (`docs/518-packet-capture-strong-export-recipient-acceptance-boundary.md`).
- stronger packet export is now destination-bound too: the approved `action.destination` tuple must align with normalized `transport.receipt.destination`, `transport.acceptance.receipt.recipient`, and `export.receipt.destination` rather than letting recipient drift hide behind a valid artifact digest (`docs/519-packet-capture-strong-export-destination-bound-approval-boundary.md`).
- stronger packet recipient acceptance is now digest-confirming too: `acceptance.remote_artifact_digest` must echo the same normalized digest instead of merely pointing at a plausible remote object (`docs/520-packet-capture-strong-export-recipient-digest-confirmation-boundary.md`).
- stronger packet closure is now remote-object-continuous too: `transport.receipt.result.remote_id`, `transport.acceptance.receipt.acceptance.remote_reference`, and `export.receipt.adapter.remote_id` must stay on the same remote object identifier instead of drifting across multiple attachments or portal objects in the same case (`docs/521-packet-capture-strong-export-remote-object-continuity-boundary.md`).
- stronger packet closure is now remote-validator-continuous too: `transport.receipt.result.remote_validator`, `transport.acceptance.receipt.acceptance.remote_validator`, and `export.receipt.adapter.remote_validator` must stay on the same remote validator instead of collapsing the stronger proof chain back to object id alone (`docs/522-packet-capture-strong-export-remote-validator-continuity-boundary.md`).
- stronger packet closure is now remote-protection-shaped too: `transport.acceptance.receipt.acceptance.remote_protection` and `export.receipt.adapter.remote_protection` must stay on the same remote protection posture so the stronger chain does not call recipient acceptance “durable evidence” without a typed overwrite/delete-resistance claim (`docs/523-packet-capture-strong-export-remote-protection-posture-boundary.md`).
- stronger packet closure is now remote-locator-continuous too: `transport.receipt.result.remote_locator`, `transport.acceptance.receipt.acceptance.remote_locator`, and `export.receipt.adapter.remote_locator` must stay on the same remote locator so the stronger chain keeps a typed breadcrumb back to the same accepted remote object instead of leaving later retrieval to portal folklore (`docs/524-packet-capture-strong-export-remote-locator-continuity-boundary.md`).
- later stronger packet evidence re-check now uses `transport.reverification.receipt` as a metadata-only follow-up lane: keep `reverification.body_downloaded = false` and preserve the same accepted remote validator / protection posture / locator instead of re-downloading packet bytes or hand-auditing portal UI state (`docs/525-packet-capture-strong-export-remote-reverification-boundary.md`).

## Operational guidance

- Keep `uri_hint` in receipts redacted and non-secret.
- Prefer ticketing transports (attachments) over random uploads: they bind sharing to a case id.
- For OOB exports (USB/offline), require a “human protocol” step and still emit a receipt.

See: `rfcs/RFC-0187-policy-constrained-transports.md`.

Last updated: 2026-03-09r254
