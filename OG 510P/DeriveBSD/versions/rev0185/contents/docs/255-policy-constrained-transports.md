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

This separation helps in audits:
- export policy: what we *intended* to allow
- transport policy: what destinations we *actually* permit
- transport receipt: what *happened*

## Operational guidance

- Keep `uri_hint` in receipts redacted and non-secret.
- Prefer ticketing transports (attachments) over random uploads: they bind sharing to a case id.
- For OOB exports (USB/offline), require a “human protocol” step and still emit a receipt.

See: `rfcs/RFC-0187-policy-constrained-transports.md`.
