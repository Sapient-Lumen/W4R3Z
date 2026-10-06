# Publish-session path prefixes stay URI-path-safe

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace

`net.publish.session` already says that `published_endpoint.path_prefix` is the typed path half of the
canonical `relay-url` endpoint tuple, and the archive already keeps that path absolute and normalized.

One smaller ambiguity still remained inside the path string itself.

> if the typed path is already canonical, what keeps it from carrying raw spaces, backslashes, or
> percent-encoded reserved characters such as `%2F` and `%2E` that make later readers guess whether
> they should compare bytes, compare decoded text, or apply filesystem-style cleanup?

If the archive leaves that open, the same receipt can still be “normalized” on paper while support,
UI, export, and future implementation disagree about whether the typed path needs another decode step
before it is actually comparable.

See `adrs/ADR-0175-publish-session-path-prefixes-stay-uri-path-safe.md`.

## Boundary

`published_endpoint.path_prefix` now stays **URI-path-safe** as already-serialized receipt state.

### No percent-encoding in the typed path field

If present, `published_endpoint.path_prefix` must not carry percent-encoding at all.

That means the typed path floor can no longer hide delimiter-looking or dot-looking bytes behind `%xx`
text and then rely on later readers to decide whether decoding should happen before comparison or
routing.

### No raw spaces or backslashes

If present, `published_endpoint.path_prefix` must also stay free of raw spaces and backslashes.

That keeps the typed path floor aligned with ordinary URI path grammar instead of turning it into a
copy/paste cleanup lane or a filesystem-style path string.

### The typed path stays the serialized comparison surface

ADR-0169 already keeps `published_endpoint.url_hint` and `published_endpoint.path_prefix` tied to the
same canonical endpoint tuple, and ADR-0172 already keeps the typed path absolute + normalized.

This decision narrows the remaining path-string grammar: `path_prefix` now stays as the already-
serialized comparison surface, not a bucket that still needs percent-decoding or raw-space cleanup
before use.

## What this prevents

### No hidden `%2F` or `%2E` semantics in the typed path field

A share can no longer say the typed path is canonical while still letting `%2F`, `%2E`, or similar
reserved/dot-looking escapes decide meaning only after a later decode step.

### No “looks like a URL path, acts like a filesystem path” drift

A share can no longer keep a typed path with backslashes or raw spaces and expect support/UI/export to
guess how that should be rendered, escaped, or compared.

### No second path-comparison ladder beside the receipt

The archive no longer teaches one path rule for the typed receipt and another for whichever future
reader happens to parse or decode it more aggressively.

## Why this is the right floor now

This is intentionally small.
It does **not** decide the full Unicode policy for path segments, final pretty-printing, or richer
routing objects.
It only keeps the existing typed path field from reopening percent-decoding and cleanup ambiguity after
the archive already chose that field as the canonical review surface.

That is enough to make eventual implementation, support, and evidence handling more coherent without
widening the architecture.

## Wire-up points

- `spec/net.publish.session.schema.json`
- `spec/examples/net.publish.session.json`
- `tools/check_publish_session_path_prefix_uri_safe_contract.py`
- `tools/check_publish_session_path_prefix_contract.py`
- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/579-publish-session-url-hints-follow-endpoint-tuple.md`
- `docs/582-publish-session-path-prefixes-stay-normalized.md`

## Related

- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/579-publish-session-url-hints-follow-endpoint-tuple.md`
- `docs/582-publish-session-path-prefixes-stay-normalized.md`
- `docs/583-publish-session-relay-url-hints-stay-https-shaped.md`
- `docs/32-curated-references.md`

Last updated: 2026-03-19r315
