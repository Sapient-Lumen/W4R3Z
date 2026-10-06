# ADR-0182: Publish-session binding hints stay lane-exact

- Status: Accepted
- Date: 2026-03-20

## Context

ADR-0163 already made audience-binding hints explicit in one direction:
`organization-users` and `provider-identity` temporary sharing require
`published_endpoint.audience.identity_provider_hint`, and `named-recipients` requires
`published_endpoint.audience.recipient_hint`.

One smaller but still expensive ambiguity remained:

**what keeps a receipt from carrying `identity_provider_hint` or `recipient_hint` even when the
rest of the audience lane says it is not an IdP-bound or named-recipient share at all?**

Without one more narrow decision, public links, support-peer handoffs, tailnet publication, and
secret-only shares can still borrow binding-hint prose and tell two competing stories about what
kind of audience boundary actually held.

DeriveBSD does not need a broader generic “binding note” field here, but it does need
`identity_provider_hint` and `recipient_hint` to stay the typed evidence clues they already
became.

## Decision

1. `published_endpoint.audience.identity_provider_hint` now follows
   `published_endpoint.audience.authn_mode` exactly.
2. If `audience.authn_mode = provider-identity`, `identity_provider_hint` remains required.
3. If `identity_provider_hint` is present, `audience.authn_mode` must therefore be
   `provider-identity`.
4. `published_endpoint.audience.recipient_hint` now follows
   `published_endpoint.audience.class` exactly.
5. If `audience.class = named-recipients`, `recipient_hint` remains required.
6. If `recipient_hint` is present, `audience.class` must therefore be `named-recipients`.
7. This ADR does **not** invent a generic hint object for all publish-session audience classes.
   If future product work needs some other typed audience clue, it should arrive as a new
   lane-specific field instead of overloading the existing binding hints.

## Consequences

- Non-IdP lanes can no longer carry `identity_provider_hint` “just in case.”
- Non-recipient lanes can no longer carry `recipient_hint` as a spare human-readable note.
- Receipts, trusted UI, and support bundles can read `identity_provider_hint` and
  `recipient_hint` as exact evidence about the audience lane instead of soft commentary.

## Alternatives considered

- **Leave binding hints optional outside their lanes.** Rejected because it lets receipts mix
  audience-binding prose into lanes that are supposed to stay public, support-session, or
  tailnet-shaped.
- **Treat the hints as generic explanatory notes.** Rejected because that would turn typed evidence
  back into comment slots.
- **Invent a broader binding-hints object now.** Rejected as too wide for this round.
