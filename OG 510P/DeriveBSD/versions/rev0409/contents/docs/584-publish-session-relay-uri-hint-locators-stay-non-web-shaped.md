# Publish-session relay uri-hint locators stay non-web-shaped

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace

`net.publish.session` already says which temporary-sharing lane gets a relay-side `uri-hint`, and it
already keeps the outward copy surface web-shaped through `published_endpoint.url_hint`.

One smaller ambiguity still remained inside the relay-side URI lane.

> if the public copy surface is already the `relay-url` endpoint hint, what keeps `relay.remote_locator.value`
> from becoming a second `http` / `https` URL field instead of a relay-scoped locator?

If the archive leaves that open, the same receipt can carry a canonical published endpoint tuple, a
copyable outward `https` URL, and then a second web-looking relay-side locator that support/UI/export must
still explain.

See `adrs/ADR-0174-publish-session-relay-uri-hint-locators-stay-non-web-shaped.md`.

## Boundary

Relay-side `uri-hint` locators now stay **non-web-shaped**.

### `uri-hint` remains URI-shaped, but not `http` / `https`

If `relay.remote_locator.kind = uri-hint`, then `relay.remote_locator.value` must still be an absolute
URI-shaped locator, but its scheme must not be `http` or `https`.

That keeps the relay-side locator as a relay/control-plane hint instead of letting it collapse into a
second copy of the published web endpoint.

### `uri-hint` must stay free of userinfo, query, and fragment

If `relay.remote_locator.kind = uri-hint`, then `relay.remote_locator.value` must not carry userinfo,
query material, or fragment material.

That keeps the relay-side locator evidence-shaped instead of teaching credential-looking or bearer-token
locator folklore.

### `destination_hint` inherits the same floor in the `uri-hint` lane

ADR-0168 already requires optional `relay.destination_hint` to equal `relay.remote_locator.value`
exactly when `kind = uri-hint`.

That means the same non-web-shaped relay-locator floor now applies to the adjacent display hint too:
`destination_hint` can no longer reintroduce an `https` URL or userinfo/query/fragment decoration in the
same lane.

## What this prevents

### No second public web URL beside `published_endpoint.url_hint`

A `relay-url` share can no longer keep the outward endpoint tuple/web hint coherent while also rendering
its relay-side locator as another `https` URL.

### No credential-looking relay locator forms

The relay-side locator can no longer carry `userinfo@...` decoration or query/fragment baggage in the
same surface support and export tooling may copy.

### No ambiguous relay-versus-public endpoint story

Support/UI/export no longer need to explain why the public endpoint and relay-side locator both look like
canonical web URLs for the same share.

## Why this is the right floor now

This is intentionally small.
It does **not** choose a provider registry, final relay URI schemes, or richer relay endpoint objects.
It only keeps the existing `uri-hint` lane from collapsing back into the already-separate outward web
endpoint surface.

That is enough to shrink ambiguity again without widening the architecture.

## Wire-up points

- `spec/net.publish.session.schema.json`
- `spec/examples/net.publish.session.json`
- `tools/check_publish_session_remote_locator_uri_hint_contract.py`
- `tools/check_publish_session_remote_locator_value_contract.py`
- `tools/check_publish_session_destination_hint_contract.py`
- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/577-publish-session-relay-remote-locator-values-follow-locator-kind.md`
- `docs/578-publish-session-destination-hint-follows-remote-locator.md`

## Related

- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/576-publish-session-relay-remote-locator-kind-follows-access-model.md`
- `docs/577-publish-session-relay-remote-locator-values-follow-locator-kind.md`
- `docs/578-publish-session-destination-hint-follows-remote-locator.md`
- `docs/579-publish-session-url-hints-follow-endpoint-tuple.md`
- `docs/583-publish-session-relay-url-hints-stay-https-shaped.md`
- `docs/32-curated-references.md`

Last updated: 2026-03-19r314
