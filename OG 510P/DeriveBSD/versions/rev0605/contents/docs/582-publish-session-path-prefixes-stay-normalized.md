# Publish-session path prefixes stay normalized

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace

`net.publish.session` already says which temporary-sharing lanes may carry typed endpoint paths at all,
it already keeps `url_hint` / `path_prefix` paired, and it already keeps the host half of the published
tuple honestly host-shaped.

One smaller ambiguity still remained inside the path half of that tuple.

> if `published_endpoint.path_prefix` is already the typed path floor, what keeps it from being
> `/hooks//demo`, `/./hooks`, or `/hooks/../admin` and forcing later normalization guesses?

If the archive leaves that open, a receipt can still look coherent while support, CLI, UI, and later
implementation disagree about what the path really means once separator collapse or dot-segment removal
enters the picture.

See `adrs/ADR-0172-publish-session-path-prefixes-stay-normalized.md`.

## Boundary

`published_endpoint.path_prefix` now stays a **normalized absolute path prefix**.

### `path_prefix` is path-only typed state

If present, `published_endpoint.path_prefix` must:
- start with `/`,
- stay free of query / fragment material,
- stay free of repeated `/` separators,
- and stay free of `.` / `..` path segments.

This keeps the field a reviewable typed path surface instead of a string that still needs hidden cleanup
rules.

### `url_hint` must carry that same normalized path

For `relay-url` shares, `published_endpoint.url_hint` still has to carry the same path as
`published_endpoint.path_prefix`.
Now that path must also already be normalized.

That keeps the copyable URL surface and the typed path surface coherent without making future readers
replay dot-segment removal or separator-collapse logic just to understand a receipt.

### What this still does not decide

This is intentionally narrow.
It does **not** decide:
- scheme defaults,
- trailing-slash semantics,
- or richer endpoint objects.

ADR-0175 now narrows the remaining path-string grammar further by keeping percent-encoding, raw spaces, and backslashes out too; see `docs/585-publish-session-path-prefixes-stay-uri-path-safe.md`.

It only keeps the existing path field from becoming the next cheap drift seam.

## What this prevents

### No repeated-separator drift

A share can no longer say the canonical path is `/hooks//demo` and leave later readers to guess whether
that was intentional or accidental.

### No dot-segment folklore in the typed path field

A share can no longer encode `/hooks/../admin` or `/./hooks` inside `published_endpoint.path_prefix`
and still pretend the typed endpoint tuple is already canonical.

### No path-normalization disagreement between export and implementation

Support bundles, receipts, CLI views, and future implementation no longer need a second unwritten rule
about whether the typed path field should be normalized before use.

## Wire-up points

- `spec/net.publish.session.schema.json`
- `spec/examples/net.publish.session.json`
- `tools/check_publish_session_path_prefix_contract.py`
- `tools/check_publish_session_url_hint_contract.py`
- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/575-publish-session-endpoint-hints-follow-access-model.md`
- `docs/579-publish-session-url-hints-follow-endpoint-tuple.md`
- `docs/585-publish-session-path-prefixes-stay-uri-path-safe.md`

## Related

- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/575-publish-session-endpoint-hints-follow-access-model.md`
- `docs/579-publish-session-url-hints-follow-endpoint-tuple.md`
- `docs/581-publish-session-published-endpoint-hostnames-stay-host-shaped.md`
- `docs/32-curated-references.md`

Last updated: 2026-03-19r315
