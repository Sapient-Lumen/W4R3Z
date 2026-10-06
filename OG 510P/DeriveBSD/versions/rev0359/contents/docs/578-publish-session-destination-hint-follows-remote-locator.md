# Publish-session destination hint follows remote locator

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace

`net.publish.session` already says which relay-side locator kinds belong to each temporary-sharing lane and what
value grammar those locator kinds are allowed to carry.

One smaller but still expensive ambiguity remained in the adjacent display field.

> once relay-side locator kind and value are coherent, can `relay.destination_hint` still contradict them?

If the archive leaves that open, URL-shaped publication can still expose two drifting relay-side copy surfaces,
while support-session or tailnet publication can still smuggle a URL-looking destination through a supposedly non-
URI relay lane.

See `adrs/ADR-0168-publish-session-destination-hint-follows-remote-locator.md`.

## Boundary

`relay.destination_hint` now follows the relay locator posture too.

### `uri-hint` shares get exactly one copyable relay-side hint

If `relay.remote_locator.kind = uri-hint` and `relay.destination_hint` is present, then
`relay.destination_hint` must equal `relay.remote_locator.value` exactly.

That keeps URL-shaped publication from carrying two different relay-side strings that operators, UI, support
bundles, or docs might each treat as the “real” destination.

### Non-URI relay lanes keep `destination_hint` non-URI-shaped

If `relay.remote_locator.kind = portal-object`, `object-path`, or `opaque`, then any optional
`relay.destination_hint` must stay non-URI-shaped.

At the archive floor, that means it must not contain `://`.

This is intentionally conservative. DeriveBSD still does **not** standardize provider-specific support-code or
object-path display grammar here. It only prevents non-URI lanes from quietly reintroducing URL folklore through
an adjacent hint field.

## Why this is the right floor now

This keeps three relay-side stories coherent without inventing a bigger adapter registry:
- URL-shaped publication keeps one canonical copyable relay-side string,
- support-peer handoff may still carry human-facing object/code hints, but not hidden URLs,
- and private tailnet/device sharing may still carry display text, but it stays object/path shaped.

That is enough to sharpen the spec and preserve explainability without standardizing every provider UX. `docs/579-publish-session-url-hints-follow-endpoint-tuple.md` then makes the published-endpoint `url_hint` / `path_prefix` family equally coherent inside the `relay-url` lane, so the user-facing URL surface does not drift even after the relay-side destination text is fixed.

## Wire-up points

- `spec/net.publish.session.schema.json`
- `spec/examples/net.publish.session.json`
- `tools/check_publish_session_destination_hint_contract.py`
- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/576-publish-session-relay-remote-locator-kind-follows-access-model.md`
- `docs/577-publish-session-relay-remote-locator-values-follow-locator-kind.md`
- `docs/584-publish-session-relay-uri-hint-locators-stay-non-web-shaped.md`
- `docs/579-publish-session-url-hints-follow-endpoint-tuple.md`

## Related

- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/570-publish-session-access-model-posture-boundary.md`
- `docs/571-publish-session-tailnet-reverse-forward-posture-boundary.md`
- `docs/576-publish-session-relay-remote-locator-kind-follows-access-model.md`
- `docs/577-publish-session-relay-remote-locator-values-follow-locator-kind.md`
- `docs/286-inbound-listen-broker-and-firewall-leases.md`
- `docs/460-inbound-listen-posture-by-profile.md`

Last updated: 2026-03-19r314
