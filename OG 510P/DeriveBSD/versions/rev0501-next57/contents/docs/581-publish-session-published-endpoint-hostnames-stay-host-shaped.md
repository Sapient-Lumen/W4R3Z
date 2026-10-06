# Publish-session published-endpoint hostnames stay host-shaped

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace

`net.publish.session` already decided which temporary-sharing lanes carry `hostname + port`, and it
already requires `relay-url` URL hints to serialize that same tuple.

One smaller ambiguity still remained inside the tuple itself.

> if `hostname + port` is already canonical, what keeps `published_endpoint.hostname` from being a URL,
> a `host:port` string, a path-bearing token, or a localhost-style source name?

If the archive leaves that open, the supposedly typed host half of the published endpoint is still just
an arbitrary string that support, CLI, and implementation must reparse.

See `adrs/ADR-0171-publish-session-published-endpoint-hostnames-stay-host-shaped.md`.

## Boundary

`published_endpoint.hostname` now stays a **lowercase host-shaped token**.

### `hostname` is not a serialized URL or authority

If `published_endpoint.hostname` is present, it must not carry:
- a scheme-bearing prefix,
- userinfo,
- an explicit `:port`,
- a path,
- query or fragment material,
- or bracketed authority decoration.

The canonical published endpoint is still split as typed state:
- `hostname`
- `port`
- and, in the `relay-url` lane, optional `url_hint` / `path_prefix` that serialize the same tuple.

That keeps the host token reviewable without reparsing URL syntax out of it.

### `hostname` stays non-local

If present, `published_endpoint.hostname` must not be:
- `localhost`,
- a name under `.localhost`,
- or a loopback IP literal.

That keeps the published side of the receipt distinct from the local-source side.
`local_service.service_uri_hint` is the place where loopback/local debugging hints may appear, and even
there it now has to stay loopback-shaped and secret-clean; see
`docs/580-publish-session-local-service-uri-hints-stay-loopback-shaped.md`.

### `hostname` stays DNS-host-shaped

For now the field stays intentionally conservative: lowercase ASCII dot-separated labels using letters,
digits, and hyphen.

That is enough for relay/public names, documentation/example names such as `example.invalid`, and the
private reverse-forward/device-name lane, without reopening case-normalization or authority-parsing
questions.

## What this prevents

### No URL-smuggling in the canonical host field

A share can no longer claim it has a canonical `hostname + port` endpoint while the `hostname` field
itself contains the full relay URL instead of just the hostname token.

### No hidden port drift inside `hostname`

A share can no longer encode `preview-7c3f.relay.example.invalid:443` inside `hostname` and still carry
`port = 443` separately.

### No source/public collapse through localhost text

A share can no longer keep the local source loopback-only while its published endpoint names
`localhost`, `preview.localhost`, or `127.0.0.1` as if those were real outward publication targets.

## Why this is the right floor now

This is intentionally small.
It does **not** standardize provider-owned relay names, custom DNS, or richer typed endpoint objects.
It only makes the existing `published_endpoint.hostname` field honest about being a hostname.

That is enough to shrink ambiguity again without widening the architecture.

## Wire-up points

- `spec/net.publish.session.schema.json`
- `spec/examples/net.publish.session.json`
- `tools/check_publish_session_hostname_contract.py`
- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/575-publish-session-endpoint-hints-follow-access-model.md`
- `docs/571-publish-session-tailnet-reverse-forward-posture-boundary.md`

## Related

- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/575-publish-session-endpoint-hints-follow-access-model.md`
- `docs/579-publish-session-url-hints-follow-endpoint-tuple.md`
- `docs/580-publish-session-local-service-uri-hints-stay-loopback-shaped.md`
- `docs/571-publish-session-tailnet-reverse-forward-posture-boundary.md`
- `docs/32-curated-references.md`

Last updated: 2026-03-19r311
