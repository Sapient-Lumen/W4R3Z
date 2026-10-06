# Publish-session URL hints follow endpoint tuple

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace

`net.publish.session` already says which temporary-sharing lanes may carry URL hints at all, and it
already keeps the relay-side locator story coherent.

One smaller but still expensive ambiguity remained inside the `relay-url` lane itself.

> once `relay-url` shares already carry canonical `hostname + port`, can `url_hint` and `path_prefix`
> still tell a different endpoint story?

If the archive leaves that open, the same receipt can carry one host/port tuple, a different copyable
URL hint, and a third path string that support or UI has to guess how to reconcile.

See `adrs/ADR-0169-publish-session-url-hints-follow-endpoint-tuple.md`.

## Boundary

For `published_endpoint.access_model = relay-url`, the optional URL-hint family now has to serialize
one coherent endpoint tuple.

### `url_hint` and `path_prefix` travel together

If `published_endpoint.url_hint` is present, `published_endpoint.path_prefix` must also be present.
If `published_endpoint.path_prefix` is present, `published_endpoint.url_hint` must also be present.

That keeps the receipt from carrying a copyable URL without the typed path it is supposed to mean, or
from carrying a bare path string with no serialized URL surface beside it.

### `url_hint` must serialize the canonical host and port

For `relay-url`, `published_endpoint.url_hint` must be an absolute URI-shaped hint with an authority
component.
Its host and explicit port must match `published_endpoint.hostname` and `published_endpoint.port` exactly.

This keeps `hostname + port` authoritative while still allowing a copyable serialized URL surface.
The receipt no longer has to choose between “the tuple fields are real” and “the pasted URL string is
real.” The outward hint now also stays https-shaped with no userinfo, so the URL-shaped lane no longer carries a weaker or more ambiguous transport story than the typed tuple; see `docs/583-publish-session-relay-url-hints-stay-https-shaped.md`. That outward tuple now also stays lease-frozen for one bounded share, so a changed copyable URL surface must mint a fresh `session_id` and `authority.lease_id` instead of silently repointing the same share; see `docs/594-publish-session-published-endpoint-surface-stays-lease-frozen.md`.

### `path_prefix` must equal the parsed URL path

For `relay-url`, the parsed path of `published_endpoint.url_hint` must equal
`published_endpoint.path_prefix` exactly.

That keeps the path floor reviewable and queryable as typed state instead of leaving it trapped inside
one serialized URL string. `published_endpoint.path_prefix` now also stays normalized and URI-path-safe, so the typed
path surface itself cannot carry repeated separators, `.` / `..` path segments, percent-encoding, raw spaces, or
backslashes that still need cleanup logic; see `docs/582-publish-session-path-prefixes-stay-normalized.md` and `docs/585-publish-session-path-prefixes-stay-uri-path-safe.md`.

## What this prevents

### No host/port drift between tuple and copyable URL

A `relay-url` share can no longer claim `hostname = preview-7c3f.relay.example.invalid` and `port =
443` while its `url_hint` serializes some other authority.

### No path drift between `path_prefix` and serialized URL

A `relay-url` share can no longer carry `path_prefix = /hooks/demo` while the actual serialized
`url_hint` points somewhere else.

### No half-present URL-hint family

A URL-shaped share can no longer carry only `url_hint` or only `path_prefix` and leave support/UI to
infer the missing half.

## Why this is the right floor now

This is intentionally small.
It does **not** standardize final scheme vocabulary, URL prettification, or richer typed endpoint
objects.
It only requires the existing optional URL-hint family to serialize the same endpoint tuple the receipt
already says is canonical, with a normalized `path_prefix` as the typed path floor. That tuple is now also the lease-frozen outward surface for one bounded share rather than a mutable hint family under the same lease.

That is enough to make eventual implementation, export, and support more coherent without front-loading
provider-specific design.

## Wire-up points

- `spec/net.publish.session.schema.json`
- `spec/examples/net.publish.session.json`
- `tools/check_publish_session_url_hint_contract.py`
- `docs/575-publish-session-endpoint-hints-follow-access-model.md`
- `docs/578-publish-session-destination-hint-follows-remote-locator.md`
- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`

## Related

- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/570-publish-session-access-model-posture-boundary.md`
- `docs/575-publish-session-endpoint-hints-follow-access-model.md`
- `docs/576-publish-session-relay-remote-locator-kind-follows-access-model.md`
- `docs/577-publish-session-relay-remote-locator-values-follow-locator-kind.md`
- `docs/578-publish-session-destination-hint-follows-remote-locator.md`
- `docs/286-inbound-listen-broker-and-firewall-leases.md`
- `docs/460-inbound-listen-posture-by-profile.md`
- `docs/582-publish-session-path-prefixes-stay-normalized.md`

Last updated: 2026-03-20r324