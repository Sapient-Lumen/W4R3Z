# Publish-session binding hints stay lane-exact

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace

`net.publish.session` already tightened audience-bound sharing in one direction:
`organization-users` / `provider-identity` shares must name `identity_provider_hint`, and
`named-recipients` shares must name `recipient_hint`.

One smaller ambiguity still remained:

> what keeps a receipt from carrying `identity_provider_hint` or `recipient_hint` even when the
> rest of the audience lane says the share is public-link, support-session, tailnet, or secret-only?

If the archive leaves that open, receipts can still carry binding-hint prose that does not match
the actual audience lane and tell two competing stories about what boundary held.

See `adrs/ADR-0182-publish-session-binding-hints-stay-lane-exact.md`.

## Boundary

`published_endpoint.audience.identity_provider_hint` and
`published_endpoint.audience.recipient_hint` now stay **exact with their lanes**.

### Provider-identity lanes still require `identity_provider_hint`

If `published_endpoint.audience.authn_mode = provider-identity`, then
`published_endpoint.audience.identity_provider_hint` remains required.

That preserves the already-accepted IdP-bound floor for organization-user, named-recipient, and
provider-identity webhook shares.

### Non-provider-identity lanes must not carry `identity_provider_hint`

If `published_endpoint.audience.authn_mode` is any of:

- `none`
- `support-session`
- `tailnet-identity`
- `single-use-secret`
- `shared-secret`

then `published_endpoint.audience.identity_provider_hint` must be absent.

That keeps public-link, support-peer, tailnet, and secret-only receipts from borrowing IdP prose as
if some second invisible provider gate existed.

### Named-recipient lanes still require `recipient_hint`

If `published_endpoint.audience.class = named-recipients`, then
`published_endpoint.audience.recipient_hint` remains required.

That preserves the already-accepted named-binding floor.

### Non-named-recipient lanes must not carry `recipient_hint`

If `published_endpoint.audience.class` is any of:

- `public-link`
- `public-webhook`
- `organization-users`
- `support-session-peer`
- `tailnet-users`

then `published_endpoint.audience.recipient_hint` must be absent.

That keeps recipient prose from drifting onto group, callback, support-peer, or private tailnet
shares as a spare audience note.

### Binding hints are inverse evidence too

If a publish session carries `identity_provider_hint`, the receipt must therefore also be on a
`provider-identity` lane.
If a publish session carries `recipient_hint`, the receipt must therefore also be a
`named-recipients` lane.

A `public-link` share cannot carry an IdP hint on the side,
and an `organization-users` share cannot carry a recipient note that makes it read like a hidden
single-recipient exception.

## What this prevents

### No public or secret-only share with a hidden IdP story

`public-link`, `public-webhook` with `shared-secret`, and secret-only `named-recipients` shares now
stay explained by their actual auth lane instead of carrying IdP prose beside it.

### No organization-user share with a hidden recipient exception

`organization-users` stays group/IdP-shaped instead of carrying a `recipient_hint` that makes the
receipt read like a one-off recipient carveout.

### No support/tailnet share borrowing human-share binding notes

`support-session-peer` and `tailnet-users` now keep their own typed posture instead of carrying
human-share binding hints that point at some different audience model.

## Why this is the right floor now

This is intentionally small.
It does **not** define a generic audience-binding metadata object for every share class.
It only keeps `identity_provider_hint` and `recipient_hint` meaning one thing everywhere the
archive surfaces them.

That is enough to make receipts, policy, trusted UI, and support bundles more coherent without
widening the architecture.

## Wire-up points

- `spec/net.publish.session.schema.json`
- `spec/examples/net.publish.session.json`
- `tools/check_publish_session_binding_hint_exactness_contract.py`
- `docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md`
- `docs/573-publish-session-audience-bound-shares-require-binding-hints.md`

## Related

- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md`
- `docs/572-publish-session-audience-bound-human-shares-stay-relay-url-shaped.md`
- `docs/573-publish-session-audience-bound-shares-require-binding-hints.md`
- `docs/589-publish-session-secret-handoffs-follow-authn-mode.md`
- `docs/591-publish-session-validation-hints-stay-webhook-only.md`

Last updated: 2026-03-20r322
