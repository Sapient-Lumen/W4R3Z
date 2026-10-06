# RFC-0120: Portal consent receipts (auditable interactive "ask")

Status: **draft**

## Motivation

DeriveBSD portals/powerbox brokers enable mediated dynamic access without reintroducing ambient authority.

When a portal uses an interactive "ask" path (workstations/dev), it must remain:
- explainable
- reviewable
- non-forgeable

Without explicit receipts, the most privileged path in the system becomes the least accountable.

## Goals

- Define a small, signable consent receipt object.
- Prevent prompt drift by versioning prompt templates.
- Compose with existing grant + lease + revocation evidence.

## Non-goals

- Designing a complete desktop UX.
- Making interactive prompts a production dependency.
- Logging secret bytes.

## Proposal

### Evidence object: portal.consent

Add a content-addressed evidence object emitted when a decision is made via "ask":

- request digest
- prompt template id/version
- user identity (local uid + optional label)
- decision (allow/deny)
- constraints applied (ttl, scope, rights)
- optional linkage to `lease_id` and `portal.grant` digest

Schema: `spec/portal.consent.schema.json`.

### Prompt template discipline

- UI backends provide prompt templates with stable ids.
- Receipts bind to (id, version) rather than raw prompt text.

### Server mode

- headless portals emit only `portal.grant` / `portal.revoke`.
- interactive receipts are optional and policy-gated.

## Relationship to existing docs

- Portal broker: `docs/179-portals-and-powerbox.md`
- Leases + revocation: `docs/182-capability-leases-and-revocation.md`
- Explainability contract: `docs/95-explainability-contract.md`

## References

- XDG Desktop Portal overview (broker API pattern): https://flatpak.github.io/xdg-desktop-portal/
- xdg-desktop-portal repo (interfaces under org.freedesktop.portal.Desktop): https://github.com/flatpak/xdg-desktop-portal
