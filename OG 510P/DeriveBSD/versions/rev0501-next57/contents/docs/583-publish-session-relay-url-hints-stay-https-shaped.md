# Publish-session relay-url hints stay https-shaped

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace

`net.publish.session` already says which temporary-sharing lane is URL-shaped at all, and it already
keeps the `url_hint` family subordinate to the canonical `hostname + port + path_prefix` tuple.

One smaller ambiguity still remained inside the copyable outward hint.

> if a share already says `access_model = relay-url`, what keeps `published_endpoint.url_hint` from
> being `http-scheme form`, carrying `userinfo@host`, or otherwise telling a weaker/murkier transport story
> than the rest of the receipt?

If the archive leaves that open, the field people are most likely to copy, paste, screenshot, or read
aloud can still drift away from the secure relay/public-callback posture the typed endpoint tuple is
supposed to express.

See `adrs/ADR-0173-publish-session-relay-url-hints-stay-https-shaped.md`.

## Boundary

`published_endpoint.url_hint` now stays **https-shaped** in the `relay-url` lane.

### `url_hint` is an `https` URL hint, not a generic URI bucket

If `published_endpoint.access_model = relay-url` and `published_endpoint.url_hint` is present, it must:
- use literal lowercase `https` scheme syntax,
- carry an authority with a host,
- and remain free of query and fragment material.

That keeps the outward copy surface aligned with the relay-backed web/callback share posture instead of
letting the receipt quietly normalize an `http` scheme or other generic URI schemes as equally good.

### `url_hint` must not carry userinfo

If present, `published_endpoint.url_hint` must not carry `userinfo@host` authority decoration.

That keeps the copy surface from obscuring the real authority token, and it avoids teaching credential-
looking or phishing-shaped URL forms as normal publication evidence.

### The typed tuple stays authoritative

This decision does **not** change the earlier tuple boundary.
`published_endpoint.hostname`, `published_endpoint.port`, and `published_endpoint.path_prefix` still stay
canonical typed state, and `url_hint` still has to serialize the same host/port/path story rather than a
second one.

This doc only narrows the URL-shaped hint itself so the already-copyable surface tells the same transport
story as the rest of the receipt.

## What this prevents

### No outward relay share rendered as `http-scheme form`

A `relay-url` share can no longer say the canonical endpoint is relay-backed/public-facing while the
actual copyable hint is still `http-scheme form`.

### No `userinfo@host` authority obscuring the real endpoint

A share can no longer hide the real host behind `user@host` decoration in the exact field most likely to
show up in chat, support notes, exports, or screenshots.

### No second transport story beside the typed endpoint tuple

Support/UI no longer need to explain why the typed tuple reads like a secure outward share while the URL
hint reads like a weaker or more ambiguous one.

## Why this is the right floor now

This is intentionally small.
It does **not** standardize prettified display names, default-port elision, percent-encoding
normalization, or richer endpoint objects.
It only keeps the existing outward URL hint honest about being the secure URL-shaped share lane.

That is enough to make eventual implementation and evidence handling more coherent without widening the
architecture.

## Wire-up points

- `spec/net.publish.session.schema.json`
- `spec/examples/net.publish.session.json`
- `tools/check_publish_session_https_url_hint_contract.py`
- `tools/check_publish_session_url_hint_contract.py`
- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/575-publish-session-endpoint-hints-follow-access-model.md`
- `docs/579-publish-session-url-hints-follow-endpoint-tuple.md`

## Related

- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/575-publish-session-endpoint-hints-follow-access-model.md`
- `docs/579-publish-session-url-hints-follow-endpoint-tuple.md`
- `docs/581-publish-session-published-endpoint-hostnames-stay-host-shaped.md`
- `docs/582-publish-session-path-prefixes-stay-normalized.md`
- `docs/32-curated-references.md`

Last updated: 2026-03-19r314
