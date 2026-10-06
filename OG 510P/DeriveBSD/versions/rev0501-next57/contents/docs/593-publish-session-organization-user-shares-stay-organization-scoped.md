# Publish-session organization-user shares stay organization-scoped

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace

`net.publish.session` already tightened the ordinary organization-user lane in two directions:
`organization-users` shares stay `relay-url` shaped, and they must name
`identity_provider_hint` on the `provider-identity` lane.

One smaller ambiguity still remained:

> what keeps a receipt from saying `audience.class = organization-users` while the published
> endpoint still says `exposure_scope = internet`?

If the archive leaves that open, the same share can still read like “coworkers only” in the
audience lane while the exposure lane still reads like generic internet publication.

See `adrs/ADR-0183-publish-session-organization-user-shares-stay-organization-scoped.md`.

## Boundary

`published_endpoint.audience.class = organization-users` now implies
`published_endpoint.exposure_scope = organization`.

### Organization-user sharing now stays organization-scoped

If `published_endpoint.audience.class = organization-users`, then
`published_endpoint.exposure_scope` must be `organization`.

That keeps the already-typed organization-user lane from quietly collapsing back into ordinary
internet publication.

### The lane still stays IdP-bound and URL-shaped

This decision stacks on the earlier ones; it does not replace them.
Organization-user shares still require:

- `published_endpoint.access_model = relay-url`
- `published_endpoint.audience.authn_mode = provider-identity`
- `published_endpoint.audience.identity_provider_hint`

So the organization-user lane now reads as one coherent posture instead of three adjacent partial
clues.

### `named-recipients` exposure is still intentionally open

This cut is intentionally narrower than “all human-share exposure is solved.”
It does **not** decide whether `named-recipients` always compiles to `organization`, always
compiles to `internet`, or can legitimately use either depending on internal versus external
recipient posture.

The archive is only fixing the contradiction in the already-typed `organization-users` lane.

## What this prevents

### No coworkers-only share labeled as generic internet publication

A receipt can no longer say “organization users via IdP” while the same endpoint still claims
`exposure_scope = internet`.

### No need for UI or support to guess which lane was authoritative

Trusted UI, support bundles, and policy review no longer need to infer whether the audience label or
exposure label was the one that “really meant it.”

### No pressure to over-decide named-recipient scope today

By narrowing only `organization-users`, the archive gains one coherent lane without forcing an early
answer on internal versus external named-recipient sharing.

## Why this is the right floor now

This is intentionally small.
It does **not** add a new audience class, define a directory substrate, or settle the full
recipient/exposure matrix.
It only makes the existing organization-user lane internally coherent.

That is enough to make implementation, policy, receipts, and trusted UI simpler without widening
the architecture.

For the canonical current-stack map over the recent `docs/593-*` through `docs/603-*` tightening cluster, see `docs/604-publish-session-current-contract-stack-and-stale-entrypoint-firewall.md` rather than relying on this local page to act as the full companion list.

## Wire-up points

- `spec/net.publish.session.schema.json`
- `spec/examples/net.publish.session.json`
- `tools/check_publish_session_organization_exposure_contract.py`
- `docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md`
- `docs/572-publish-session-audience-bound-human-shares-stay-relay-url-shaped.md`

## Related

- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md`
- `docs/572-publish-session-audience-bound-human-shares-stay-relay-url-shaped.md`
- `docs/573-publish-session-audience-bound-shares-require-binding-hints.md`
- `docs/592-publish-session-binding-hints-stay-lane-exact.md`

Last updated: 2026-03-20r334
