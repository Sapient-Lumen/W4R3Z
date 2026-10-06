# ADR-0168: Publish-session destination hints follow remote locator

- Status: Accepted
- Date: 2026-03-19

## Context

ADR-0166 fixed the **relay-side locator kind grammar** for `net.publish.session`, and ADR-0167 fixed the
**relay-side locator value grammar**. That left one smaller but still expensive ambiguity:

**can `relay.destination_hint` quietly contradict or exceed the relay locator the receipt already chose?**

Without one more narrow decision, URL-shaped publication can still carry two different copyable relay-side
strings (`destination_hint` vs `remote_locator.value`), while support-peer or tailnet shares can still hide a
URL-looking destination in `destination_hint` even after the archive already decided those lanes are not URL-
shaped.

Current products often expose a second display string here for convenience, but leaving that field unconstrained
would reopen the same ambiguity the archive just paid to close on `relay.remote_locator.*`.

DeriveBSD does not need a provider-specific connect-command or display-template registry yet, but it does need the
optional relay-side destination hint to stop contradicting the relay locator it sits next to.

## Decision

1. `relay.destination_hint` remains optional, evidence-only adapter text.

2. If `relay.remote_locator.kind = uri-hint` and `relay.destination_hint` is present, then
   `relay.destination_hint` must equal `relay.remote_locator.value` exactly.

3. If `relay.remote_locator.kind = portal-object`, `object-path`, or `opaque`, and
   `relay.destination_hint` is present, then it must stay non-URI-shaped. In particular, it must not contain
   `://`.

4. This ADR does not standardize provider-specific display labels, support-code grammars, or final connect-command
   UX beyond that floor.

## Consequences

- URL-shaped temporary sharing now has one canonical relay-side copy surface instead of two drifting strings.
- Support-peer and tailnet lanes can no longer hide a URL-looking destination in an otherwise non-URI relay lane.
- The archive keeps the adapter surface small: it only constrains `destination_hint` enough to preserve the relay-
  side shape already decided elsewhere.

## Alternatives considered

- **Leave `destination_hint` as free text.** Rejected because it would reopen the same relay-side ambiguity that
  ADR-0166 and ADR-0167 just narrowed.
- **Delete `destination_hint` entirely.** Rejected for now; some adapters may still want an explicit display field,
  but it must not contradict the typed relay locator.
- **Standardize full provider-specific destination templates now.** Rejected as premature.
