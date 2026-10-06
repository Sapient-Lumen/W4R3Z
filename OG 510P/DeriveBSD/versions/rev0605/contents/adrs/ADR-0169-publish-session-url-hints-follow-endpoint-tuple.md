# ADR-0169: Publish-session URL hints follow endpoint tuple

- Status: Accepted
- Date: 2026-03-19

## Context

ADR-0165 fixed the **endpoint-hint family** for `net.publish.session` by deciding that only
`relay-url` shares may carry `published_endpoint.url_hint` / `path_prefix`, while `relay-url` and
`reverse-forward` both keep `hostname + port` as the canonical endpoint floor.
ADR-0166 through ADR-0168 then made the relay-side locator and destination fields coherent.

That still left one smaller but practical ambiguity on the published-endpoint side:

**can `published_endpoint.url_hint`, `path_prefix`, and `hostname + port` quietly disagree even when
all of them are present on the same `relay-url` share?**

Without one more narrow decision, a receipt can still carry a copyable URL hint whose host, port, or
path differs from the canonical tuple the same receipt claims is authoritative. That turns support
bundles, CLI output, and later implementation into a guessing game about which field is supposed to
win.

DeriveBSD does not need a provider registry or scheme taxonomy here, but it does need one coherent
rule for how the optional URL hint family relates to the already-canonical endpoint tuple.

## Decision

1. For `published_endpoint.access_model = relay-url`, `published_endpoint.hostname` and
   `published_endpoint.port` remain the canonical endpoint tuple.

2. If `published_endpoint.url_hint` is present, then `published_endpoint.path_prefix` must also be
   present.

3. If `published_endpoint.path_prefix` is present, then `published_endpoint.url_hint` must also be
   present.

4. For `relay-url`, `published_endpoint.url_hint` must be an absolute URI-shaped hint with an
   authority component, and that authority must encode the same host and explicit port carried in the
   canonical endpoint tuple.

5. For `relay-url`, the parsed path of `published_endpoint.url_hint` must equal
   `published_endpoint.path_prefix` exactly.

6. This ADR still does not standardize final scheme choice, provider-specific pretty-printing,
   percent-encoding normalization policy, or richer typed endpoint objects.

## Consequences

- URL-shaped temporary sharing now has one coherent published-endpoint story instead of three nearby
  strings that can drift.
- Support, CLI, UI, and export surfaces can treat `hostname + port + path_prefix` as the same share
  that `url_hint` serializes, rather than reopening relay dashboards or chat history.
- The archive sharpens the contract without forcing more adapter-specific decisions than it needs.

## Alternatives considered

- **Leave `url_hint` / `path_prefix` free to drift from `hostname + port`.** Rejected because that
  would keep the user-facing URL family ambiguous even after the archive already paid to make the
  surrounding fields coherent.
- **Delete `url_hint` and `path_prefix` entirely.** Rejected for now; URL-shaped shares still benefit
  from a copyable serialized hint, but it must serialize the same endpoint tuple the receipt already
  carries.
- **Standardize scheme/provider templates now.** Rejected as premature.
