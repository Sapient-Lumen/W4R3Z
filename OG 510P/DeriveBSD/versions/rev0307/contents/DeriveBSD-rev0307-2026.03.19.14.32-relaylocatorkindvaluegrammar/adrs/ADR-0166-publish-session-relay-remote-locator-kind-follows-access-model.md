# ADR-0166: Publish-session relay remote locator kind follows access model

- Status: Accepted
- Date: 2026-03-19

## Context

ADR-0165 fixed the **endpoint-hint grammar** for `net.publish.session`: URL-shaped temporary shares now
carry `hostname + port`, private tailnet sharing stays `reverse-forward`, and support-session handoff
stays `peer-relay` without pretending to be a public URL.

That still leaves one quiet escape hatch:

**can `relay.remote_locator.kind` keep reintroducing the wrong share shape even after
`published_endpoint.*` was made coherent?**

Without one more small decision, a support-peer handoff can still carry a relay-side `uri-hint`, a
private tailnet reverse-forward share can still look like a portal/session object, and the archive
ends up with one grammar on `published_endpoint` plus a second contradictory grammar on the relay
join itself.

Current products split these lanes in practice:
- URL publication often has a directly copyable URI or hostname,
- support/session handoff often centers a provider/session object or support code,
- and private forwarding/service sharing often points at a device/service object rather than a
  public URL.

DeriveBSD does not need a provider-specific remote-object registry yet, but it does need the relay
side of the receipt to stop contradicting the access model it already chose.

## Decision

1. If `published_endpoint.access_model = peer-relay`, then `relay.remote_locator.kind` must be
   `portal-object` or `opaque`.

2. If `published_endpoint.access_model = reverse-forward`, then `relay.remote_locator.kind` must be
   `object-path` or `opaque`.

3. If `relay.remote_locator.kind = uri-hint`, then `published_endpoint.access_model` must be
   `relay-url`.

4. `destination_hint` remains evidence-only adapter text. This ADR does not standardize provider
   object ids, support codes, or connect-command templates.

5. Product-shape posture is fixed as follows:
   - **B (`workstation`)** and **C (`general_os`)** keep one coherent relay-side locator story:
     URL shares may expose a URI-shaped remote locator, support-peer handoff stays portal/session
     shaped, and tailnet/device-name sharing stays object-path shaped.
   - **A (`fleet_host`)** and **D (`appliance_factory`)** gain a smaller forensic surface for any
     exceptional temporary share because the relay-side locator no longer reopens URL/session drift.

## Consequences

- Support-peer publication can no longer smuggle a URL-shaped remote locator back into the receipt
  after `peer-relay` was already chosen.
- Private tailnet reverse-forward sharing can no longer look like a provider portal/session object
  when the archive already decided it is not a support/session lane.
- URL-shaped publication stays easy to implement, but the URI-shaped remote locator lane is now
  explicitly the `relay-url` lane instead of an ambient convenience field.

## Why this is narrow enough

This ADR does **not** define:
- a provider-specific remote-object schema,
- a final connect-command UX,
- or a broader adapter registry for every relay backend.

It only binds the existing `relay.remote_locator.kind` vocabulary back to the already-accepted
access-model split.
