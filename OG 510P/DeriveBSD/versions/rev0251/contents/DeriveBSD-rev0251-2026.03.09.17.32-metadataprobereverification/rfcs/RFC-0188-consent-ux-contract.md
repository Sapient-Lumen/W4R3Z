# RFC-0188: Consent UX contract

## Problem

DeriveBSD relies on mediated, timeboxed authority (portals + leases).
But approval UX differs wildly (GUI prompts, TTY prompts, OOB approvals), and without a uniform evidence object
we lose auditability and composability.

## Proposal

Introduce two small evidence artifacts:

- `consent.request` (`spec/consent.request.schema.json`)
- `consent.receipt` (`spec/consent.receipt.schema.json`)

And standardize how high-risk actions request approvals:
- export portal emits a consent.request; tooling waits for a consent.receipt
- export.receipt can reference consent_receipt_digest
- same pattern applies to breakglass, tracing, confirmable change-sets, and posture changes

## Requirements

- Support GUI, TTY, and OOB responders
- Support two-person approval and approver allowlists
- Support secure-attention requirements when applicable
- Keep receipts metadata-only (no secrets)

See also: `docs/256-consent-ux-contract.md`.
