# Publish-session tailnet reverse-forward posture boundary

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace

`net.publish.session` already says when a temporary share is public URL-shaped and when it is
 support-peer/session-shaped.
The remaining inconsistency was the private tailnet lane.

> if a publish session already says `tailnet-users`, `tailnet-identity`, and
> `tailnet-device-name`, can it still pretend to be a URL-shaped relay share?

If the archive leaves that open, private tailnet sharing inherits public tunnel vocabulary even
 after public callback/demo sharing was already separated into the explicit internet lane.

See `adrs/ADR-0161-publish-session-tailnet-shares-stay-reverse-forward-shaped.md`.

## Boundary

Tailnet temporary sharing is now explicitly **reverse-forward/device-name shaped**. That now also means the receipt carries `hostname + port` rather than URL-only hints, and `published_endpoint.hostname` itself stays a lowercase host-shaped token instead of a pasted URL or localhost-style name; see `docs/575-publish-session-endpoint-hints-follow-access-model.md` and `docs/581-publish-session-published-endpoint-hostnames-stay-host-shaped.md`.

If any tailnet signal appears on `net.publish.session`, the access model must agree:

- `exposure_scope = tailnet` → `access_model = reverse-forward`
- `audience.class = tailnet-users` → `access_model = reverse-forward`
- `audience.authn_mode = tailnet-identity` → `access_model = reverse-forward`
- `locator_posture = tailnet-device-name` → `access_model = reverse-forward`

The archive also keeps those tailnet signals aligned the other way around:

- `tailnet-users` is not valid as a vague audience class on some other exposure scope,
- `tailnet-identity` is not valid as generic auth prose on some other exposure scope,
- and `tailnet-device-name` is not a naming trick for a URL-shaped publication lane.
- `reverse-forward` now also keeps `url_hint` / `path_prefix` absent, so the private lane names a device/service endpoint instead of masquerading as a public URL.
- `relay.remote_locator.kind` now also stays `object-path` or `opaque`, so the private lane does not regress into portal/session relay folklore either.

## What this prevents

### No URL-shaped vocabulary for private tailnet sharing

A tailnet share can no longer say `relay-url` while also claiming `tailnet-users` or a tailnet
 device name.
That keeps the private share lane honest in receipts, logs, and support bundles.

### No accidental public/internet flattening

The archive already says `public-link` and `public-webhook` are the URL-shaped publication cases.
This boundary prevents the private tailnet lane from quietly drifting back onto that same wording.

### No forced full matrix too early

This boundary still does **not** decide `organization-users` or `named-recipients`.
It only closes the inconsistency around tailnet sharing, where the archive already had enough
 posture signals to make a clean decision.

## Product-shape reading

### A — fleet host

Private mesh-style admin access can stay exceptional and bounded without teaching fleet publication
 to speak in public-share URLs.

### B — workstation

Tailnet sharing stays simple: share to the private device-name lane rather than mentally modeling
 it as a public tunnel URL that merely happens to require tailnet identity.

### C — general OS

Developer/admin private sharing stays distinct from public callback/demo flows, which keeps the
 eventual UX and evidence model easier to reason about.

### D — appliance factory / regulatory

Lab or maintenance tailnet publication stays visibly private-network shaped, which is easier to
 review than a receipt that looks like an internet-facing URL share.

## Schema surface

See:

- schema: `spec/net.publish.session.schema.json`
- example: `spec/examples/net.publish.session.json`
- locator posture: `docs/565-publish-session-session-scoped-locator-posture-boundary.md`
- access-model posture: `docs/570-publish-session-access-model-posture-boundary.md`
- endpoint-hint posture: `docs/575-publish-session-endpoint-hints-follow-access-model.md`
- relay remote-locator posture: `docs/576-publish-session-relay-remote-locator-kind-follows-access-model.md`

The schema now binds tailnet posture to `reverse-forward` and rejects tailnet/public-shape mixes. Relay-side `relay.remote_locator.value` now follows that split too: `object-path` values stay non-URI-shaped, so the private tailnet lane cannot quietly regress to URL-looking relay value text (`docs/577-publish-session-relay-remote-locator-values-follow-locator-kind.md`). Optional `relay.destination_hint` now follows that same split too, so any tailnet display text also stays non-URI-shaped instead of quietly reintroducing public-share URL folklore (`docs/578-publish-session-destination-hint-follows-remote-locator.md`).
The guardrail then validates synthetic tailnet examples so future edits cannot drift back to
 `relay-url` wording for the private tailnet lane.

## Related docs

- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/565-publish-session-session-scoped-locator-posture-boundary.md`
- `docs/570-publish-session-access-model-posture-boundary.md`
- `docs/286-inbound-listen-broker-and-firewall-leases.md`
- `docs/576-publish-session-relay-remote-locator-kind-follows-access-model.md`
- `docs/577-publish-session-relay-remote-locator-values-follow-locator-kind.md`
- `docs/578-publish-session-destination-hint-follows-remote-locator.md`
- `docs/460-inbound-listen-posture-by-profile.md`

Last updated: 2026-03-19r311