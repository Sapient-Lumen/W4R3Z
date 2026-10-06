# Publish-session audience binding and publicness posture boundary

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace

`net.publish.session` already fixed *how* temporary sharing happens:
keep the source service local-first, route through an approved relay/transport path,
and bind the act to explicit authority evidence.

The next ambiguity is smaller but operationally expensive:

> when a published endpoint is on the internet, is it for anyone, for coworkers,
> for a support peer, for one named recipient, or just for a webhook callback?

If the archive leaves that implicit, "temporary share" quietly regresses to
"paste a bearer URL into chat and hope".
See `adrs/ADR-0153-publish-session-audience-binding-and-publicness-posture.md`.

## The hard decision

A relay-backed publish session must carry an explicit audience posture.

That posture now lives in `net.publish.session.published_endpoint.audience` and records:

- `class` — the intended audience category
- `authn_mode` — how requests are expected to prove they belong to that audience

This keeps the contract adapter-neutral while refusing to let `internet` mean
"anonymous public" by default.

## Audience classes

The archive now recognizes six publish-session audience classes:

- `tailnet-users`
- `organization-users`
- `named-recipients`
- `support-session-peer`
- `public-webhook`
- `public-link`

These are intentionally small.
They name the posture difference the archive needs without inventing a recipient database or a new identity substrate.

## Authn modes

A publish session also records one auth mode:

- `tailnet-identity`
- `provider-identity`
- `support-session`
- `single-use-secret`
- `shared-secret`
- `none`

This is not meant to standardize every provider protocol.
It is the minimum summary needed for receipts, explain surfaces, and policy posture.

## Required bindings

The schema now fixes several combinations as non-negotiable:

### Tailnet/private sharing stays tailnet-identified

If `published_endpoint.exposure_scope = tailnet`, then:

- `audience.class = tailnet-users`
- `audience.authn_mode = tailnet-identity`

This keeps private-network sharing from being described as generic "internet relay" behavior.

### Support-peer sharing stays support-session-bound

If `published_endpoint.exposure_scope = support-peer`, then:

- `audience.class = support-session-peer`
- `audience.authn_mode = support-session`

That keeps support handoffs aligned with the existing support-session authority lane instead of turning them into freestanding public URLs. ADR-0159 then makes that alignment exact rather than implied as a support-session authority join: support-peer publication must use `authority.trigger = support-session` and carry `authority.support_session_digest` as the proof of which support session justified the share.

### Public bearer URLs are an explicit exception

If `audience.class = public-link`, then:

- `published_endpoint.exposure_scope` must be `internet`
- `audience.authn_mode` must be `none`

That means a fully public temporary URL is still possible, but it is no longer the default interpretation of internet publication.
It is a named stronger exception. Even then, the locator posture for public/org/support shares remains `session-scoped`; a stable or reserved public hostname is still the durable-ingress problem, not the temporary-sharing contract. Because `public-link` is explicitly `authn_mode = none`, it also now keeps `published_endpoint.secret_handoff` absent instead of carrying a contradictory secret lane; see `docs/589-publish-session-secret-handoffs-follow-authn-mode.md`.

### Webhook publication is a different exception

If `audience.class = public-webhook`, then:

- `published_endpoint.exposure_scope` must be `internet`
- `audience.authn_mode` must be `shared-secret` or `provider-identity`
- `audience.validation_hint` is required
- if `audience.validation_hint` is present, `audience.class` must stay `public-webhook`

This keeps callback testing viable without pretending webhook reachability and human preview sharing are the same posture, and it keeps the receipt explicit about what the receiver was supposed to validate. If the webhook is `provider-identity` gated, it now also keeps `secret_handoff` absent so the auth story stays singular instead of quietly carrying both IdP and secret lanes; see `docs/574-publish-session-public-webhook-shares-require-validation-hints.md` and `docs/589-publish-session-secret-handoffs-follow-authn-mode.md`.

### Access-model posture must agree with audience posture

Audience posture now also constrains the share shape:

- `public-link` and `public-webhook` require `published_endpoint.access_model = relay-url`
- `organization-users` and `named-recipients` also require `published_endpoint.access_model = relay-url`
- `support-peer` / `support-session-peer` / `support-session` require `published_endpoint.access_model = peer-relay`

That keeps ordinary authenticated preview/demo sharing and public callback/demo publication visibly URL-shaped while keeping support publication visibly peer/session-shaped. See `docs/570-publish-session-access-model-posture-boundary.md` and `docs/572-publish-session-audience-bound-human-shares-stay-relay-url-shaped.md`.

### Human preview sharing should stay audience-bound

For human-facing temporary shares:

- `organization-users` now also requires `published_endpoint.exposure_scope = organization`
- `organization-users` requires `provider-identity` and `identity_provider_hint`
- `named-recipients` requires `provider-identity` or `single-use-secret`, and also requires `recipient_hint`
- any `provider-identity` posture also requires `identity_provider_hint`

So the normal answer for preview/demo/support-style sharing is now:
**auth-gated or recipient-bound first; public link only by explicit stronger choice.**
Non-secret authn modes must not carry `secret_handoff`, so the typed `authn_mode` lane stays the whole receiver proof story rather than a partial summary beside a second hidden secret lane; see `docs/589-publish-session-secret-handoffs-follow-authn-mode.md`.

See `docs/573-publish-session-audience-bound-shares-require-binding-hints.md` for the exact audience-bound binding-hint floor. `organization-users` now also stays organization-scoped instead of claiming generic internet publication; see `docs/593-publish-session-organization-user-shares-stay-organization-scoped.md`. Those binding hints are now inverse evidence too: `identity_provider_hint` must stay on `provider-identity` lanes and `recipient_hint` must stay on `named-recipients` lanes instead of drifting onto public-link, support-peer, tailnet, or secret-only receipts; see `docs/592-publish-session-binding-hints-stay-lane-exact.md`. `public-webhook` also now requires `validation_hint`, and non-webhook share classes must keep `validation_hint` absent so the field stays webhook-only evidence instead of a generic note slot; see `docs/574-publish-session-public-webhook-shares-require-validation-hints.md` and `docs/591-publish-session-validation-hints-stay-webhook-only.md`.

## Product-shape posture

### A — fleet host

Use durable brokered services for real publication.
For temporary sharing, prefer `support-session-peer` or tightly bounded `organization-users` flows.
`public-link` is out of baseline posture, and `public-webhook` is exceptional integration/support tooling.

### B — workstation

The ergonomic share path remains relay-backed publish sessions,
but the default human share should be `organization-users`, `named-recipients`, or `support-session-peer`.
A `public-link` is an explicit stronger action, not the assumed meaning of "share this local app".

### C — general OS

The same default applies.
`public-webhook` is allowed for explicit admin/developer workflows, but the archive still distinguishes callback endpoints from human preview sharing.

### D — appliance factory / regulatory

Shipped posture stays off `public-link`.
Any `public-webhook` or other internet publication remains lab/maintenance-only unless a narrower compliance story is accepted later.

## What this deliberately does not decide

This boundary does **not** choose:

- the exact SSO/OAuth provider,
- the final `identity_provider_hint` vocabulary or recipient roster shape,
- the full recipient list model,
- a universal remote-acceptance receipt,
- or the exact trusted-UI text for public-link warnings.

Those are implementation or later-boundary questions.
The archive only fixes the missing posture vocabulary.

## Why this matters for coherence

Current relay ecosystems already distinguish private-network sharing,
auth-gated sharing, and public publication.
DeriveBSD should preserve that distinction in its evidence surface.
Otherwise the archive will say "relay-backed" while operators still have to guess whether a share was private, audience-bound, or globally reachable.

By naming the audience posture directly, `net.publish.session` becomes implementable enough for policy, trusted UI, receipts, and forensics without forcing all provider choices up front. The share must also stay no-auto-resume and reboot-cleared, so a public-link or webhook test cannot quietly survive as a remembered background tunnel.

## Related docs

- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/286-inbound-listen-broker-and-firewall-leases.md`
- `docs/564-publish-session-end-conditions-and-no-auto-resume-posture-boundary.md`
- `docs/460-inbound-listen-posture-by-profile.md`
- `docs/255-policy-constrained-transports.md`
- `docs/291-remote-assistance-sessions-as-evidence.md`
- `docs/249-lease-registry-and-cross-lane-revocation.md`
- `docs/570-publish-session-access-model-posture-boundary.md`
- `docs/572-publish-session-audience-bound-human-shares-stay-relay-url-shaped.md`
- `docs/574-publish-session-public-webhook-shares-require-validation-hints.md`
- `docs/589-publish-session-secret-handoffs-follow-authn-mode.md`

Last updated: 2026-03-20r323
