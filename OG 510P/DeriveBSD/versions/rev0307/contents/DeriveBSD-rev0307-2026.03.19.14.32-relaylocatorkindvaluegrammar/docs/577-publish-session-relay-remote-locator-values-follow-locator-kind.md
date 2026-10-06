# Publish-session relay remote locator values follow locator kind

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace

`net.publish.session` already says which **relay-side locator kinds** belong to each temporary-
sharing lane:
- `relay-url` may use `uri-hint`,
- `peer-relay` stays `portal-object` / `opaque`,
- `reverse-forward` stays `object-path` / `opaque`.

One expensive ambiguity still remained inside the value itself.

> once relay-side locator kinds are coherent, can `relay.remote_locator.value` still sneak URI grammar back into the wrong lane?

If the archive leaves that open, support-session or tailnet publication can still carry a hidden
URI-looking value even while the receipt claims the share is portal/object/path shaped.

See `adrs/ADR-0167-publish-session-relay-remote-locator-values-follow-locator-kind.md`.

## Boundary

Relay-side locator **values** now follow **locator kind** too.

### `uri-hint` values stay URI-shaped and locator-only

If `relay.remote_locator.kind = uri-hint`, then `relay.remote_locator.value` must be URI-shaped.
It stays locator-only evidence, so query strings and fragments remain out.

### `portal-object`, `object-path`, and `opaque` values stay non-URI-shaped

If `relay.remote_locator.kind = portal-object`, `object-path`, or `opaque`, then
`relay.remote_locator.value` must stay non-URI-shaped.

At the archive level, that means it must not contain `://`.

This is intentionally conservative: DeriveBSD still does **not** standardize provider-specific
support-code or object-path syntax here. It only forbids non-URI lanes from smuggling URI-looking
values back in.

## Why this is the right floor now

This keeps three product stories coherent without overcommitting the implementation:
- public callback/demo sharing can stay copyable-URI shaped,
- support-session handoff can stay support-code / portal-object shaped,
- and private tailnet/device sharing can stay object/path shaped.

That is enough to sharpen the spec and preserve explainability without forcing a provider registry.

## Wire-up points

- `spec/net.publish.session.schema.json`
- `spec/examples/net.publish.session.json`
- `tools/check_publish_session_remote_locator_value_contract.py`
- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/576-publish-session-relay-remote-locator-kind-follows-access-model.md`

## Related

- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/570-publish-session-access-model-posture-boundary.md`
- `docs/571-publish-session-tailnet-reverse-forward-posture-boundary.md`
- `docs/575-publish-session-endpoint-hints-follow-access-model.md`
- `docs/576-publish-session-relay-remote-locator-kind-follows-access-model.md`
- `docs/286-inbound-listen-broker-and-firewall-leases.md`
- `docs/460-inbound-listen-posture-by-profile.md`

Last updated: 2026-03-19r307
