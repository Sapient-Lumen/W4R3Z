# ADR-0162: Publish-session audience-bound human shares stay relay-url-shaped

- Status: Accepted
- Date: 2026-03-19

## Context

ADR-0152 introduced `net.publish.session` so temporary sharing could stop collapsing into shadow
 tunnels or casual public listeners.
ADR-0160 then fixed the first access-model split: public callback/demo publication stays
 `relay-url` shaped, while support-peer publication stays `peer-relay` shaped.
ADR-0161 fixed the private tailnet lane too, so `tailnet-users` / `tailnet-identity` /
 `tailnet-device-name` now stay `reverse-forward` shaped.

One ambiguity still remained in the ordinary human-sharing lane:

**if a publish session already says `organization-users` or `named-recipients`, is it still
 allowed to describe itself as a peer-relay or reverse-forward share?**

Leaving that open would keep the archive internally expensive.
The same receipt could claim:
- this is a normal audience-bound human preview/demo share,
- but the access-model wording still looks like a support-session peer handoff,
- or it borrows private tailnet/device-name vocabulary that no longer matches how the share is
  consumed.

Current ecosystems already show the split DeriveBSD needs here: identity-gated published apps in
 Cloudflare Access and auth-gated ngrok endpoints are still URL-shaped endpoints even when the
 audience is restricted.
DeriveBSD needs the same typed distinction without choosing a single provider or recipient model.

## Decision

1. Audience-bound human temporary sharing becomes an explicit **relay-url** lane.

2. If either of the following is true, then `published_endpoint.access_model` must be
   `relay-url`:
   - `published_endpoint.audience.class = organization-users`
   - `published_endpoint.audience.class = named-recipients`

3. This completes the first useful access-model matrix for temporary sharing:
   - `organization-users` → `relay-url`
   - `named-recipients` → `relay-url`
   - `public-link` / `public-webhook` → `relay-url`
   - `support-session-peer` → `peer-relay`
   - `tailnet-users` → `reverse-forward`

4. This ADR does **not** decide the full recipient/identity model.
   In particular, it does **not** choose:
   - the exact provider identity protocol,
   - whether `named-recipients` is always organization-local or may include external recipients,
   - the final trusted-UI copy flow,
   - or the exact relay/transport adapter implementation.

5. This ADR only says that ordinary audience-bound human sharing is no longer allowed to masquerade
   as support-session peer-relay posture or private tailnet reverse-forward posture in the archive
   evidence model.

## Consequences

- Auth-gated preview/demo sharing stays visibly URL-shaped in receipts and support bundles.
- Support-peer remains the only peer/session-shaped human handoff lane.
- Tailnet remains the private device-name / reverse-forward lane.
- The archive gets a cleaner eventual implementation target because every current audience class now
  maps to one of the three accepted access-model shapes.

## Why this is narrow enough

This ADR does **not** define:
- a provider-specific link format,
- a new identity subsystem,
- a recipient directory,
- or a durable ingress story for audience-bound human sharing.

It only makes the remaining audience-bound human share postures agree with the access-model
 surface.
