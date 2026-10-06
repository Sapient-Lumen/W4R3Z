# ADR-0153: Publish-session audience binding and publicness posture

- Status: Accepted
- Date: 2026-03-19

## Context

ADR-0152 introduced `net.publish.session` so temporary sharing could stop collapsing into
shadow tunnels or casual public listeners.
That still left one expensive ambiguity open:

**what does a temporary published endpoint mean about who may reach it?**

A relay URL on the public internet can mean very different things:

- a support peer bound to an existing support session,
- coworkers authenticated through an organization identity layer,
- a small named-recipient preview handoff,
- a public webhook callback,
- or an actually public bearer URL.

If those stay collapsed, "internet" quietly becomes "anonymous public by default".
That would make B/C temporary sharing drift back toward shadow-tunnel folklore,
while A/D would lose the distinction between bounded temporary sharing and real publication posture.

The adapter ecosystem already shows the split:
- some relay paths stay identity-bound or org-scoped,
- some are tailnet/private-network scoped,
- and some intentionally expose an unauthenticated public endpoint for callbacks or general sharing.

DeriveBSD needs one small archive-level answer that names those postures without choosing a single provider.

## Decision

1. `net.publish.session.published_endpoint` now requires an `audience` object.

2. The audience object records two facts:
   - `class`: the intended audience posture
   - `authn_mode`: how requests are expected to bind to that audience

3. The allowed `audience.class` values are:
   - `tailnet-users`
   - `organization-users`
   - `named-recipients`
   - `support-session-peer`
   - `public-webhook`
   - `public-link`

4. The allowed `audience.authn_mode` values are:
   - `tailnet-identity`
   - `provider-identity`
   - `support-session`
   - `single-use-secret`
   - `shared-secret`
   - `none`

5. The following bindings are now part of the contract:
   - `exposure_scope = tailnet` implies `audience.class = tailnet-users`
     and `audience.authn_mode = tailnet-identity`
   - `exposure_scope = support-peer` implies `audience.class = support-session-peer`
     and `audience.authn_mode = support-session`
   - `audience.class = public-link` is only valid with `exposure_scope = internet`
     and `audience.authn_mode = none`
   - `audience.class = public-webhook` is only valid with `exposure_scope = internet`
     and `audience.authn_mode` in `{shared-secret, provider-identity}`
   - `audience.class = organization-users` requires `audience.authn_mode = provider-identity`
   - `audience.class = named-recipients` requires `audience.authn_mode` in
     `{provider-identity, single-use-secret}`

6. Product-shape posture is fixed as follows:
   - **B (`workstation`)** defaults to `organization-users`, `named-recipients`, or
     `support-session-peer`; `public-link` is an explicit stronger exception.
   - **C (`general_os`)** follows the same default, while allowing `public-webhook`
     for explicit admin/developer callback workflows.
   - **A (`fleet_host`)** should treat `public-link` as out of baseline posture and
     `public-webhook` as exceptional support/integration tooling, not service publication.
   - **D (`appliance_factory`)** keeps shipped posture off `public-link`; any
     `public-webhook` or relay publication remains lab/maintenance only.

7. Relay and identity providers remain adapter territory.
   DeriveBSD standardizes the audience/publicness contract, not a specific SaaS access layer.

## Consequences

- `internet` no longer silently means "anonymous public".
- B/C preview and support sharing can stay ergonomic without normalizing bearer URLs as the default.
- Webhook testing remains possible, but it is now named as a distinct exception posture.
- A/D keep a cleaner line between temporary sharing and durable published service posture.
- Adapter receipts and UI can now explain *who this share was intended for*, not only *how it was routed*.

## Why this is narrow enough

This ADR does **not** define:
- a full recipient directory,
- a new identity subsystem,
- a remote acceptance protocol,
- or a universal relay provider abstraction.

It only adds the missing contract needed to keep temporary sharing from collapsing back into
"internet URL == public by default".
