# ADR-0163: Publish-session audience-bound shares require binding hints

- Status: Accepted
- Date: 2026-03-19

## Context

ADR-0153 made `net.publish.session` carry an explicit audience class and auth mode.
ADR-0162 then finished the first useful access-model matrix, so ordinary audience-bound human
sharing now stays `relay-url` shaped instead of borrowing support-peer or tailnet vocabulary.

One ambiguity still remained inside the audience posture itself:

**what keeps `organization-users`, `named-recipients`, and `provider-identity` from becoming
 hand-wavy labels in receipts instead of evidence-shaped audience bindings?**

Without one more small decision, the archive can still emit a publish session that says:
- this share was for `organization-users`,
- or this was for `named-recipients`,
- or requests authenticated through `provider-identity`,

while still forcing later operators and support bundles to guess which identity provider or
recipient binding actually held the boundary.

Current products already expose that distinction. Cloudflare Access policies can be scoped by
validated email selectors and identity-provider groups, and ngrok's OAuth-protected preview flows
can deny requests unless the authenticated email or domain matches an explicit allowlist.
DeriveBSD does not need to standardize those providers, but it does need receipts to stop saying
"audience-bound" without naming the binding hint that made that audience real.

## Decision

1. Audience-bound publish sessions now require **binding hints** on the receipt surface.

2. If `published_endpoint.audience.authn_mode = provider-identity`, then
   `published_endpoint.audience.identity_provider_hint` is required.

3. If `published_endpoint.audience.class = organization-users`, then
   `published_endpoint.audience.identity_provider_hint` is also required.
   The share may still remain adapter-neutral, but it must say which identity-provider posture
   held the organization-user boundary.

4. If `published_endpoint.audience.class = named-recipients`, then
   `published_endpoint.audience.recipient_hint` is required.
   This remains evidence-only metadata describing the intended recipient binding; it is not a new
   recipient-directory or address-book subsystem.

5. This ADR does **not** require the full recipient roster, a provider-specific group id, or the
   final trusted-UI roster picker.
   It only says that audience-bound shares must stop presenting audience labels without the minimum
   binding hint that makes those labels explainable.

## Consequences

- `organization-users` shares can now say which identity-provider posture held the audience gate.
- `named-recipients` shares can now say who the recipient binding was aimed at without reopening
  chat logs or out-of-band messages.
- `provider-identity` stops being a generic auth label with no clue about which IdP policy surface
  was involved.
- The archive gets a better implementation target for explain surfaces and support bundles without
  choosing a specific provider or recipient-directory subsystem.

## Why this is narrow enough

This ADR does **not** define:
- the exact provider protocol,
- the exact format of recipient rosters,
- whether recipients are internal-only or may be external,
- or a new identity catalog.

It only keeps audience-bound temporary sharing evidence-shaped by requiring binding hints where the
archive already claimed a recipient or identity boundary existed.
