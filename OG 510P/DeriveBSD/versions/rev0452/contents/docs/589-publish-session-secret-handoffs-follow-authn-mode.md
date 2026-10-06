# Publish-session secret handoffs follow authn_mode

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace

`net.publish.session` already tightened the secret-gated lane in one direction:
if a share uses `single-use-secret` or `shared-secret`, the usable secret must travel on
`published_endpoint.secret_handoff` instead of hiding in a URL.

One smaller ambiguity still remained:

> what keeps a receipt from carrying `published_endpoint.secret_handoff` even when the typed
> `audience.authn_mode` says the share is `none`, `provider-identity`, `support-session`, or
> `tailnet-identity`?

If the archive leaves that open, a `public-link`, IdP-gated preview share, or support peer handoff
can still carry an extra secret object and tell two competing stories about what the receiver was
actually expected to present.

See `adrs/ADR-0179-publish-session-secret-handoffs-follow-authn-mode.md`.

## Boundary

`published_endpoint.secret_handoff` now follows **`audience.authn_mode` exactly**.

### Secret-gated authn modes still require the handoff

If `published_endpoint.audience.authn_mode` is either:

- `single-use-secret`
- `shared-secret`

then `published_endpoint.secret_handoff` remains required.

That preserves the already-accepted redacted-locator, bounded-lifetime, and explicit-consumption
posture.

### Non-secret authn modes must not carry a secret handoff

If `published_endpoint.audience.authn_mode` is any of:

- `none`
- `provider-identity`
- `support-session`
- `tailnet-identity`

then `published_endpoint.secret_handoff` must be absent.

That keeps the receipt from claiming one authn lane in `authn_mode` while quietly carrying a second
secret-based lane beside it.

### `secret_handoff` is inverse evidence too

If a publish session carries `published_endpoint.secret_handoff`, the share must therefore also use
`single-use-secret` or `shared-secret`.

A public link cannot quietly carry a secret blob “just in case,” and a provider-identity or
support-session share cannot smuggle an extra secret factor without the archive first choosing a new
typed posture.

## What this prevents

### No public-link receipt with a hidden secret lane

A `public-link` share now stays honestly `authn_mode = none` instead of looking public in one field
while still carrying a secret handoff object in another.

### No provider-identity share that secretly behaves like a secret-gated share

An IdP-gated preview/demo share can no longer carry `secret_handoff` beside
`authn_mode = provider-identity` and leave support/export surfaces guessing what the receiver really
had to present.

### No support-peer or tailnet share with an extra hidden credential story

`support-session` and `tailnet-identity` shares now keep their existing typed posture instead of
carrying an undeclared second secret lane on the side.

## Why this is the right floor now

This is intentionally small.
It does **not** define MFA, provider-plus-secret composition, step-up prompts, or richer receiver
policy.
It only keeps the existing `authn_mode` vocabulary singular and exact.

That is enough to make policy, trusted UI, receipts, and forensics more coherent without widening the
architecture.

## Wire-up points

- `spec/net.publish.session.schema.json`
- `spec/examples/net.publish.session.json`
- `tools/check_publish_session_secret_handoff_authn_mode_contract.py`
- `docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md`
- `docs/566-publish-session-redacted-locators-and-separate-secret-handoff-boundary.md`
- `docs/568-publish-session-secret-consumption-semantics-boundary.md`

## Related

- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md`
- `docs/566-publish-session-redacted-locators-and-separate-secret-handoff-boundary.md`
- `docs/567-publish-session-secret-handoff-lifetime-coupled-to-session-authority.md`
- `docs/568-publish-session-secret-consumption-semantics-boundary.md`

Last updated: 2026-03-19r319
