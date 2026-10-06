# ADR-0173: Publish-session relay-url hints stay https-shaped

- Status: Accepted
- Date: 2026-03-19

## Context

ADR-0165 decided that `relay-url` is the URL-shaped temporary-sharing lane.
ADR-0169 then required the optional `url_hint` / `path_prefix` family to serialize the same canonical
published endpoint tuple, and ADR-0172 kept the typed path half normalized.

That still left one smaller but practical ambiguity in the copyable URL surface itself:

**if a receipt already says the outward share is a `relay-url`, what keeps `published_endpoint.url_hint` from being `http-scheme form`, carrying `userinfo@host`, or otherwise reopening the exact sort of public-hint ambiguity the typed endpoint tuple was supposed to shrink?**

Without one more narrow decision, the archive can still produce receipts where the typed endpoint tuple
looks coherent while the public-facing copy surface quietly weakens transport expectations or hides the
real authority behind userinfo decoration.

DeriveBSD does not need a full URL-canonicalization subsystem here, but it does need one coherent rule
for the existing outward URL hint.

## Decision

1. `published_endpoint.url_hint` remains an optional convenience/evidence surface only in the
   `relay-url` lane.

2. When present for `published_endpoint.access_model = relay-url`, it must stay **https-shaped**:
   - scheme is literal lowercase `https`,
   - it carries an authority with a host,
   - it must not carry userinfo,
   - it must not carry query or fragment material,
   - and its host, port, and path stay subordinate to the already-typed `hostname`, `port`, and
     `path_prefix` fields.

3. This ADR intentionally does **not** decide stronger URL prettification, default-port elision,
   percent-encoding normalization, or richer endpoint objects.

## Consequences

- The copyable public/callback hint now tells the same transport story as the rest of the receipt.
- Support/UI/export no longer need to explain why a supposedly outward relay-backed share is rendered as
  `http-scheme form` or why the authority looked like `user@host` instead of just `host`.
- The archive keeps the URL-shaped lane practical without teaching bearer-URL or authority-obscuring
  folklore as normal receipt grammar.

## Alternatives considered

- **Leave `url_hint` as any absolute URI-shaped string.** Rejected because it preserves an easy drift
  seam in the one field people are most likely to copy, paste, screenshot, or read aloud.
- **Standardize the entire final URL normal form now.** Rejected as too wide for this round.
- **Delete `url_hint` entirely and keep only typed fields.** Rejected because the archive already wants
  a copyable/evidence URL surface for the `relay-url` lane.
