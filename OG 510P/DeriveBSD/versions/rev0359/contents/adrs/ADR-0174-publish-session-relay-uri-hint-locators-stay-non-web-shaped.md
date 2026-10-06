# ADR-0174: Publish-session relay uri-hint locators stay non-web-shaped

- Status: Accepted
- Date: 2026-03-19

## Context

ADR-0166 bound `relay.remote_locator.kind = uri-hint` to the `relay-url` lane.
ADR-0167 then required the corresponding value to stay URI-shaped, and ADR-0168 kept optional
`relay.destination_hint` subordinate to that same relay-side locator text.
ADR-0173 also made `published_endpoint.url_hint` the explicitly web-shaped outward copy surface.

That still left one smaller but practical ambiguity inside the relay-side `uri-hint` lane itself:

**if the public-facing copy surface is already `published_endpoint.url_hint`, what keeps `relay.remote_locator.value` from becoming a second `http` / `https` URL field instead of a relay-scoped locator?**

Without one more narrow decision, the archive can still emit receipts where the outward endpoint tuple and
copyable `https` URL are coherent, while the relay-side locator quietly reuses the same web URL grammar.
That would force support, export, CLI, and later implementation to guess whether the relay-side locator is
supposed to be a provider/control-plane handle or just a second copy of the published web endpoint.

DeriveBSD does not need a provider registry or a final relay-URI scheme taxonomy here, but it does need a
coherent floor for the existing `uri-hint` lane.

## Decision

1. If `relay.remote_locator.kind = uri-hint`, then `relay.remote_locator.value` remains an absolute
   URI-shaped locator surface, but it must stay **non-web-shaped**:
   - scheme must not be `http` or `https`,
   - userinfo is forbidden,
   - query and fragment material stay forbidden.

2. Because ADR-0168 already requires optional `relay.destination_hint` to equal
   `relay.remote_locator.value` exactly in the `uri-hint` lane, the same non-web-shaped floor applies to
   that adjacent relay-side display hint too.

3. This ADR intentionally does **not** standardize final provider-specific relay URI schemes, authority
   grammar, or path layout. It only keeps the relay-side locator from collapsing back into the already-
   separate public web endpoint surface.

## Consequences

- Relay-backed temporary sharing now has one coherent split:
  - `published_endpoint.url_hint` is the outward web/callback copy surface,
  - `relay.remote_locator.value` is the relay-scoped locator surface.
- Support/UI/export no longer need to explain why the relay-side locator and the public endpoint both look
  like first-class `https` URLs for the same share.
- The archive keeps the relay-side locator practical without forcing adapter-specific scheme registries yet.

## Alternatives considered

- **Allow `uri-hint` to stay any absolute URI, including `http` / `https`.** Rejected because that keeps a
  second public-web-looking locator surface beside the already-typed endpoint tuple and outward `url_hint`.
- **Standardize the final relay URI scheme taxonomy now.** Rejected as too wide for this round.
- **Delete `uri-hint` from the relay side entirely.** Rejected because the archive still wants an explicit
  typed relay-side locator surface for the `relay-url` lane.
