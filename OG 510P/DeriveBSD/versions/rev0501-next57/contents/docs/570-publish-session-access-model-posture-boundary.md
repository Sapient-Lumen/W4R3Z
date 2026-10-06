# Publish-session access-model posture boundary

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace

`net.publish.session` already says **who** the audience is, **how long** the share lasts,
which names stay session-scoped, how usable secrets stay off the locator lane, and which exact
support session justifies a support-peer handoff.

One expensive ambiguity still remained:

> does the archive know whether a temporary share is URL-shaped or peer/session-shaped,
> or are those still being flattened into one vague “relay share” story?

If the archive leaves that open, a support-session-bound handoff can still regress into
“send the support tunnel URL”, while public callback/demo sharing can drift onto peer/session
wording that no longer matches how the share is actually consumed.

See `adrs/ADR-0160-publish-session-access-model-posture-boundary.md`.

## Boundary

`net.publish.session.published_endpoint.access_model` is now a typed posture surface,
not just adapter trivia.

The archive first fixed two non-negotiable bindings here:

- `public-link` and `public-webhook` stay **URL-shaped** and therefore require
  `published_endpoint.access_model = relay-url`
- `support-peer` stays **peer/session-shaped** and therefore requires
  `published_endpoint.access_model = peer-relay`

ADR-0161 and ADR-0162 then completed the remaining audience-class shapes: private `tailnet` stays
 `reverse-forward` shaped, while `organization-users` and `named-recipients` also stay `relay-url`
 shaped.

This means the evidence surface now agrees with the already-accepted audience and authority rules:
public callback/demo sharing and ordinary audience-bound human sharing are visibly URL-oriented,
 while support handoff publication is visibly joined to a support/session lane instead of becoming a
 generic shareable URL.

## What this prevents

### No support-session tunnel-URL folklore

If a publish session says `support-peer`, or uses `support-session-peer` / `support-session`
audience posture, it cannot also say `access_model = relay-url`.
The support handoff stays peer-relay shaped all the way down. The inverse now also holds: if a
receipt claims `authority.trigger = support-session`, that trigger itself also stays on the
support-peer lane instead of justifying a non-support `relay-url` share; see `docs/588-publish-session-support-session-triggers-stay-support-peer-shaped.md`.

### No peer/session wording for public callbacks

If a publish session says `public-webhook` or `public-link`, it cannot drift onto
`access_model = peer-relay`.
That keeps callback/public-link publication visibly URL-shaped instead of pretending a webhook test
 was a peer/session handoff.

### Matrix now completes across the current audience classes

This boundary is no longer the whole story by itself.
ADR-0161 fixed the private tailnet lane in `docs/571-publish-session-tailnet-reverse-forward-posture-boundary.md`, and ADR-0162 fixes the remaining ordinary human-share lane in `docs/572-publish-session-audience-bound-human-shares-stay-relay-url-shaped.md`
- `docs/575-publish-session-endpoint-hints-follow-access-model.md`. The current audience vocabulary now has a complete access-model shape without inventing more audience classes or a bigger relay subsystem. `docs/575-publish-session-endpoint-hints-follow-access-model.md` then fixes which endpoint hints belong to each shape so URL, device-name, and support-peer handoff do not keep reusing the same mixed locator prose. `docs/576-publish-session-relay-remote-locator-kind-follows-access-model.md` now fixes the relay-side locator grammar too, so `relay.remote_locator.kind` cannot quietly contradict the chosen access model.

## Product-shape reading

### A — fleet host

Public URL-style sharing stays exceptional and support handoffs stay session-shaped, which is the
 safer default for operational and forensic review.

### B — workstation

Human support sharing no longer blurs into “copy this tunnel URL”.
If the share is support-peer, the receipt now says it was peer-relay-shaped.

### C — general OS

Webhook/demo publication remains viable, but the receipt keeps it obviously URL-shaped instead of
 pretending it is the same lane as a support peer session.

### D — appliance factory / regulatory

Exceptional temporary publication becomes easier to review because the receipt now says whether the
 operator created a URL-style callback/public share or a peer-relay support handoff.

## Schema surface

See:

- schema: `spec/net.publish.session.schema.json`
- example: `spec/examples/net.publish.session.json`
- support authority join: `docs/569-publish-session-support-peer-requires-support-session-authority-boundary.md`
- audience posture: `docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md`

The schema now binds:

- `public-link` → `relay-url`
- `public-webhook` → `relay-url`
- `organization-users` → `relay-url`
- `named-recipients` → `relay-url`
- `support-peer` / `support-session-peer` / `support-session` → `peer-relay`
- `tailnet` / `tailnet-users` / `tailnet-identity` / `tailnet-device-name` → `reverse-forward`
- endpoint hints then follow access model: `relay-url` / `reverse-forward` → `hostname + port`; `peer-relay` → no URL/host endpoint hints
- relay remote locator kinds then follow access model too: `relay-url` may stay `uri-hint`, `peer-relay` → `portal-object` / `opaque`, `reverse-forward` → `object-path` / `opaque`
- relay remote locator values then follow locator kind too: `relay.remote_locator.value` stays URI-shaped for `uri-hint`, while `portal-object` / `object-path` / `opaque` values stay non-URI-shaped so the relay value text cannot contradict the chosen lane
- optional relay destination hints then follow the relay locator too: `uri-hint` shares keep `relay.destination_hint = relay.remote_locator.value`, while `portal-object` / `object-path` / `opaque` shares keep `destination_hint` non-URI-shaped so adjacent display text cannot contradict the chosen lane
- and inside the `relay-url` lane, optional `url_hint` / `path_prefix` now travel together and must serialize the same `hostname + port + path_prefix` tuple instead of becoming a second contradictory published-endpoint story; see `docs/579-publish-session-url-hints-follow-endpoint-tuple.md`

The guardrail chain then enforces those bindings across schema, example, synthetic drift cases, and
 archive wording.

## Related docs

- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md`
- `docs/569-publish-session-support-peer-requires-support-session-authority-boundary.md`
- `docs/571-publish-session-tailnet-reverse-forward-posture-boundary.md`
- `docs/572-publish-session-audience-bound-human-shares-stay-relay-url-shaped.md`
- `docs/575-publish-session-endpoint-hints-follow-access-model.md`
- `docs/576-publish-session-relay-remote-locator-kind-follows-access-model.md`
- `docs/579-publish-session-url-hints-follow-endpoint-tuple.md`
- `docs/578-publish-session-destination-hint-follows-remote-locator.md`
- `docs/286-inbound-listen-broker-and-firewall-leases.md`
- `docs/460-inbound-listen-posture-by-profile.md`

Last updated: 2026-03-19r318
