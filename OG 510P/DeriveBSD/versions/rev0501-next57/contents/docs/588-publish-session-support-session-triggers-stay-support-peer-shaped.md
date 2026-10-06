# Publish-session support-session triggers stay support-peer-shaped

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace

`net.publish.session` already fixed the support-peer boundary in one direction:
if a share says `support-peer`, or uses `support-session-peer` / `support-session` audience
posture, it must join the exact `support.session` authority lane.

One smaller ambiguity still remained:

> what keeps a publish session from claiming `authority.trigger = support-session` while still being
> a public callback, a public link, or an ordinary audience-bound `relay-url` share?

If the archive leaves that open, support-session proof can drift into generic URL-shaped sharing and
support/export surfaces are back to guessing whether a receipt names a real support peer handoff or
just a public share wearing support vocabulary.

See `adrs/ADR-0178-publish-session-support-session-triggers-stay-support-peer-shaped.md`.

## Boundary

`authority.trigger = support-session` now implies the **full support-peer share shape**.

A publish session that claims support-session authority must also stay aligned on the published side:

- `published_endpoint.exposure_scope = support-peer`
- `published_endpoint.access_model = peer-relay`
- `published_endpoint.audience.class = support-session-peer`
- `published_endpoint.audience.authn_mode = support-session`
- `authority.support_session_digest`
- `lifecycle.end_conditions` containing `support-session-end`

That keeps support-session authority from justifying callback/demo publication, ordinary
organization-user sharing, or public-link folklore.

## What this prevents

### No support proof on a public callback share

A `public-webhook` or `public-link` share can no longer claim
`authority.trigger = support-session` while staying URL-shaped.
If the authority lane is support-session, the share itself must also stay support-peer shaped.

### No organization-user share that borrows support authority language

An ordinary audience-bound human share cannot stay `organization-users` / `provider-identity` or
`named-recipients` / `provider-identity` while claiming support-session proof.
That keeps support handoff evidence distinct from the ordinary preview/demo lane.

### No split story between authority and access model

Support-session authority can no longer coexist with `relay-url` or `reverse-forward` share shape in
one receipt.
The authority lane and the share shape now tell the same support-peer story.

## Why this is the right floor now

This is intentionally small.
It does **not** define a larger support workflow object, a maintenance-window lane, or a richer
remote-assistance approval chain.
It only makes the existing support-session publish authority vocabulary exact in both directions.

That is enough to keep support publication coherent and implementation-worthy without widening the
architecture.

## Wire-up points

- `spec/net.publish.session.schema.json`
- `spec/examples/net.publish.session.json`
- `tools/check_publish_session_support_trigger_contract.py`
- `docs/569-publish-session-support-peer-requires-support-session-authority-boundary.md`
- `docs/570-publish-session-access-model-posture-boundary.md`

## Related

- `docs/569-publish-session-support-peer-requires-support-session-authority-boundary.md`
- `docs/570-publish-session-access-model-posture-boundary.md`
- `docs/291-remote-assistance-sessions-as-evidence.md`
- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/461-remote-assistance-posture-by-profile.md`

Last updated: 2026-03-19r318
