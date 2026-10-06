# Publish-session relay remote locator kind follows access model

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace

`net.publish.session` already says what endpoint hints belong to each temporary-sharing lane:
- `relay-url` carries `hostname + port` and may carry URL hints,
- `reverse-forward` carries `hostname + port` without URL-only hints,
- `peer-relay` stays free of URL/host endpoint hints.

One expensive ambiguity still remained on the relay side of the receipt.

> once endpoint hints are coherent, can `relay.remote_locator.kind` still contradict the chosen access model?

If the archive leaves that open, support-peer handoff can still smuggle a `uri-hint` through the
relay join, while private tailnet sharing can still masquerade as a portal/session object even after
its endpoint grammar was made explicitly reverse-forward/device-name shaped.

See `adrs/ADR-0166-publish-session-relay-remote-locator-kind-follows-access-model.md`.

## Boundary

Relay-side remote locator kinds now follow **access model** too.

### `peer-relay` requires `portal-object` or `opaque`

If `published_endpoint.access_model = peer-relay`, then `relay.remote_locator.kind` must be:
- `portal-object`, or
- `opaque`

That keeps support-session peer handoff shaped like a provider/session object or an adapter-private
locator, not a hidden URI.

### `reverse-forward` requires `object-path` or `opaque`

If `published_endpoint.access_model = reverse-forward`, then `relay.remote_locator.kind` must be:
- `object-path`, or
- `opaque`

That keeps private tailnet/device-name sharing aligned with a device/service object grammar instead
of a public URL or support portal session.

### `uri-hint` implies `relay-url`

If `relay.remote_locator.kind = uri-hint`, then `published_endpoint.access_model` must be
`relay-url`.

That keeps URI-shaped remote locators in the same lane as URI-shaped publication.
The archive no longer allows a support-peer or reverse-forward share to say “not URL-shaped” on
`published_endpoint` while quietly reintroducing a URI-shaped relay locator on the back side. `docs/577-publish-session-relay-remote-locator-values-follow-locator-kind.md` then tightens the remaining loophole by requiring `relay.remote_locator.value` to follow locator kind too, `docs/584-publish-session-relay-uri-hint-locators-stay-non-web-shaped.md` keeps the `uri-hint` branch relay-scoped instead of `http` / `https` web-shaped, and `docs/578-publish-session-destination-hint-follows-remote-locator.md` keeps optional `relay.destination_hint` text from reopening the same drift beside it.

## What this prevents

### No support-peer handoff with a hidden URI-shaped relay object

A `peer-relay` support share can no longer keep `relay.remote_locator.kind = uri-hint`.
If the real share posture is peer/session shaped, the relay join has to say so too.

### No tailnet reverse-forward share with portal/session folklore

A `reverse-forward` tailnet share can no longer keep `relay.remote_locator.kind = portal-object`.
That prevents the private device-name lane from drifting into support/session relay language.

### No contradictory receipt grammar between endpoint and relay joins

The published endpoint and the relay join can no longer describe different share shapes.
That gives CLI/UI, explain surfaces, and support bundles one coherent locator story.

## Product-shape reading

### A — fleet host

Exceptional temporary sharing remains easier to review because the relay-side locator now agrees
with the access model the receipt already declared.

### B — workstation

Users and support can distinguish:
- URL-shaped publish links,
- peer/session support handoff,
- and private reverse-forward/device-name sharing,

without the relay join quietly blurring those lanes back together.

### C — general OS

Developer sharing stays practical, but eventual adapter implementations now have a smaller relay
locator grammar to implement and explain.

### D — appliance factory / regulatory

Exceptional maintenance/lab sharing becomes easier to audit because the remote locator no longer
quietly changes the story told by the endpoint/access-model fields.

## What this still does not decide

This boundary still does **not** decide:
- the final connect-command UX,
- the exact provider object ids,
- or a larger registry of adapter-specific remote locator schemas.

It only binds the existing `relay.remote_locator.kind` values back to the already-accepted
access-model split.

## Schema surface

See:

- schema: `spec/net.publish.session.schema.json`
- example: `spec/examples/net.publish.session.json`
- access-model posture: `docs/570-publish-session-access-model-posture-boundary.md`
- endpoint-hint posture: `docs/575-publish-session-endpoint-hints-follow-access-model.md`
- tailnet posture: `docs/571-publish-session-tailnet-reverse-forward-posture-boundary.md`

The schema now requires:
- `peer-relay` → `relay.remote_locator.kind ∈ {portal-object, opaque}`
- `reverse-forward` → `relay.remote_locator.kind ∈ {object-path, opaque}`
- `uri-hint` → `relay-url`

## Related docs

- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/570-publish-session-access-model-posture-boundary.md`
- `docs/571-publish-session-tailnet-reverse-forward-posture-boundary.md`
- `docs/575-publish-session-endpoint-hints-follow-access-model.md`
- `docs/286-inbound-listen-broker-and-firewall-leases.md`
- `docs/460-inbound-listen-posture-by-profile.md`
- `docs/577-publish-session-relay-remote-locator-values-follow-locator-kind.md`
- `docs/578-publish-session-destination-hint-follows-remote-locator.md`

Last updated: 2026-03-19r314
