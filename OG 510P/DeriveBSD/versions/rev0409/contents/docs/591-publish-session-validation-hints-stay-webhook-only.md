# Publish-session validation hints stay webhook-only

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace

`net.publish.session` already tightened the callback lane in one direction:
if a share says `published_endpoint.audience.class = public-webhook`,
it must also carry `published_endpoint.audience.validation_hint` so the receipt can say what the
receiver was supposed to validate.

One smaller ambiguity still remained:

> what keeps a receipt from carrying `audience.validation_hint` even when the share class is
> `public-link`, `organization-users`, `named-recipients`, or `support-session-peer`?

If the archive leaves that open, human-share or support receipts can still carry callback-validation
prose and tell two competing stories about what the receiver boundary actually was.

See `adrs/ADR-0181-publish-session-validation-hints-stay-webhook-only.md`.

## Boundary

`published_endpoint.audience.validation_hint` now stays **exact with the webhook lane**.

### Public-webhook shares still require the hint

If `published_endpoint.audience.class = public-webhook`, then
`published_endpoint.audience.validation_hint` remains required.

That preserves the already-accepted callback-verification floor.

### Non-webhook share classes must not carry it

If `published_endpoint.audience.class` is any of:

- `public-link`
- `organization-users`
- `named-recipients`
- `support-session-peer`

then `published_endpoint.audience.validation_hint` must be absent.

That keeps a non-webhook receipt from borrowing callback-verification prose as if it were a generic
security-note field.

### `validation_hint` is inverse evidence too

If a publish session carries `published_endpoint.audience.validation_hint`,
the receipt must therefore also be `audience.class = public-webhook`.

A named-recipient preview cannot carry “signature header” folklore on the side,
and a support-peer handoff cannot smuggle callback-validation language into a session/peer lane.

## What this prevents

### No human-share receipt with spare webhook prose

`organization-users` and `named-recipients` shares now stay explained by their own binding hints
instead of carrying webhook-validation language beside the actual audience boundary.

### No public-link receipt with a second hidden auth story

A `public-link` share can no longer say `authn_mode = none` while still carrying callback
verification prose that implies a second gate somewhere else.

### No support/session lane borrowing callback language

`support-session-peer` stays support/session-shaped instead of carrying a webhook-ish verification
note that makes the receipt read like a hidden callback endpoint.

## Why this is the right floor now

This is intentionally small.
It does **not** define a generic verification-hints object for every audience class.
It only keeps `validation_hint` meaning one thing everywhere the archive surfaces it.

That is enough to make receipts, policy, trusted UI, and support bundles more coherent without
widening the architecture.

## Wire-up points

- `spec/net.publish.session.schema.json`
- `spec/examples/net.publish.session.json`
- `tools/check_publish_session_validation_hint_webhook_only_contract.py`
- `docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md`
- `docs/574-publish-session-public-webhook-shares-require-validation-hints.md`

## Related

- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md`
- `docs/573-publish-session-audience-bound-shares-require-binding-hints.md`
- `docs/574-publish-session-public-webhook-shares-require-validation-hints.md`
- `docs/589-publish-session-secret-handoffs-follow-authn-mode.md`

Last updated: 2026-03-20r321
