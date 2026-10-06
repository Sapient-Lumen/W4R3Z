# ADR-0167: Publish-session relay remote locator values follow locator kind

- Status: Accepted
- Date: 2026-03-19

## Context

ADR-0166 fixed the **relay-side locator kind grammar** for `net.publish.session`: `uri-hint`
stays in the `relay-url` lane, `peer-relay` stays `portal-object` / `opaque`, and
`reverse-forward` stays `object-path` / `opaque`.

That still leaves one quiet escape hatch:

**can `relay.remote_locator.value` keep smuggling URI folklore back into non-URI lanes even after
`relay.remote_locator.kind` was typed?**

Without one more small decision, a support-session handoff can still carry
`kind = portal-object` while the value is a hidden `https://...` URL, and a private tailnet share
can still use `kind = object-path` while the value quietly looks like a public URI. The kind would
say one thing, the actual locator text would say another, and the archive would still be paying the
same implementation ambiguity later.

Current products split these lanes in practice:
- temporary/public callback and preview publication often yields a directly copyable URL,
- support-session handoff often centers a generated support code or provider/session object,
- and private service sharing often stays device/service shaped rather than URI-shaped.

DeriveBSD still does not need a provider-specific object registry here, but it does need the relay
value grammar to stop contradicting the relay kind it already chose.

## Decision

1. If `relay.remote_locator.kind = uri-hint`, then `relay.remote_locator.value` must be URI-shaped.
   It must remain a locator-only hint, so query strings and fragments stay out.

2. If `relay.remote_locator.kind = portal-object`, `object-path`, or `opaque`, then
   `relay.remote_locator.value` must stay non-URI-shaped. In particular, it must not contain
   `://`.

3. This ADR does not standardize provider-specific support-code, portal-object, or object-path
   syntax beyond that floor.

## Consequences

- The relay side of a `peer-relay` publish session can no longer hide a copyable URI inside a
  supposedly non-URI object lane.
- The relay side of a `reverse-forward` publish session can no longer quietly look public-URL-ish
  after the endpoint grammar already said it was private device/service sharing.
- The archive stays adapter-light: it only fixes the shaped/non-shaped distinction it needs for a
  coherent spec.

## Alternatives considered

- **Leave `relay.remote_locator.value` as free text.** Rejected because the relay kind would still
  be too easy to evade with URI-looking values.
- **Standardize full provider-specific object grammars now.** Rejected as premature; the archive
  only needs a conservative floor here.
