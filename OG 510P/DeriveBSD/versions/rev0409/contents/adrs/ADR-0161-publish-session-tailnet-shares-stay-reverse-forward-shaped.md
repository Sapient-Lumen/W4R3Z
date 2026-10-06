# ADR-0161: Publish-session tailnet shares stay reverse-forward-shaped

- Status: Accepted
- Date: 2026-03-19

## Context

ADR-0152 introduced `net.publish.session` so temporary sharing could stop collapsing into shadow
 tunnels or casual public listeners.
ADR-0155 then fixed locator posture so `tailnet` is the one stable-name exception through
 `published_endpoint.locator_posture = tailnet-device-name`.
ADR-0160 fixed public/support access-model posture, but intentionally left `tailnet`,
 `organization-users`, and `named-recipients` open until the archive had enough evidence to make a
 smaller decision.

One ambiguity is now expensive enough to close:

**if a publish session is private tailnet sharing with `tailnet-users`, `tailnet-identity`, and a
 tailnet device name, is that still allowed to describe itself as a URL-shaped relay share?**

Leaving that open would keep the archive internally inconsistent.
The same receipt could claim:
- `exposure_scope = tailnet`,
- `locator_posture = tailnet-device-name`,
- `audience.class = tailnet-users`,
- `audience.authn_mode = tailnet-identity`,

while still saying `access_model = relay-url`.
That would blur the private tailnet lane back into public-share vocabulary even after the archive
 already decided that public callback/demo publication is the URL-shaped case.

Current ecosystems already split this space: Tailscale documents **Serve** as sharing a local
 service with other devices in the tailnet, while **Funnel** is the separate internet-facing public
 URL path.
DeriveBSD needs the same distinction in its typed receipt surface without choosing a single mesh or
 relay provider.

## Decision

1. Tailnet temporary sharing becomes an explicit **reverse-forward/device-name** lane.

2. If any of the following is true, then `published_endpoint.access_model` must be
   `reverse-forward`:
   - `published_endpoint.exposure_scope = tailnet`
   - `published_endpoint.audience.class = tailnet-users`
   - `published_endpoint.audience.authn_mode = tailnet-identity`
   - `published_endpoint.locator_posture = tailnet-device-name`

3. Tailnet audience/access signals must now stay aligned in both directions:
   - `audience.class = tailnet-users` implies `exposure_scope = tailnet`
   - `audience.authn_mode = tailnet-identity` implies `exposure_scope = tailnet`
   - `locator_posture = tailnet-device-name` implies `exposure_scope = tailnet`

4. This ADR deliberately does **not** decide the remaining access-model matrix for
   `organization-users` or `named-recipients`.
   It only closes the inconsistency around the already-accepted tailnet lane.

5. This ADR does **not** define a specific overlay protocol, port-mapping mechanism, or user
   interface.
   It only says that private tailnet publication is no longer allowed to masquerade as a public URL
   share in the archive evidence model.

## Consequences

- Tailnet temporary sharing stays private-network/device-name shaped in receipts and support
  bundles.
- Public URL vocabulary remains reserved for the explicit internet publication postures.
- The archive gets a more coherent eventual implementation target: tailnet sharing now points
  toward a reverse-forward/device-name UX instead of a tunnel-URL UX.

## Why this is narrow enough

This ADR does **not** define:
- exact mesh routing internals,
- a specific tailnet provider,
- whether a browser, CLI, or service discovery UI is primary,
- or how future `organization-users` / `named-recipients` shares should map onto access models.

It only makes the already-accepted tailnet audience, identity, and locator postures agree with the
 access-model surface.
