# Relay-backed publish sessions for temporary service sharing

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate  

DeriveBSD already treats non-loopback listening as brokered authority.
The missing ergonomic answer was narrower:

> how does a user or operator temporarily share a local service without turning shadow tunnels,
> ad-hoc firewall edits, or public listeners into the real product surface?

This doc fixes that boundary.
See `adrs/ADR-0152-relay-backed-publish-sessions-for-temporary-service-sharing.md`.

## The hard decision

Temporary service sharing is a **relay-backed publish session**, not a casual public listener.

That means the blessed path for "show this preview", "receive this webhook", or
"hand this service to a support peer for an hour" is:

1. keep the service local-only,
2. publish it through an approved relay/transport path,
3. bind the act to explicit authority evidence and expiry,
4. and record the result as a typed `net.publish.session` envelope.

Durable host/network exposure still belongs to the existing listen-broker lane:
`net.listen.policy`, `net.listen.grant`, and `net.listen.receipt` remain the source of truth
for ordinary non-loopback services.

## Why the archive needs a separate lane

If temporary sharing is treated as "just another listener", B/C users will bypass the broker
with hosted tunnels and reverse forwards because the durable ingress path is too heavy for demos,
webhook tests, and short support handoffs.
If temporary sharing is treated as a normal developer convenience everywhere, A/D quietly inherit
workstation tunnel folklore as production posture.

`net.publish.session` is the small separation that avoids both failures.

## Contract surface

See:

- schema: `spec/net.publish.session.schema.json`
- example: `spec/examples/net.publish.session.json`

A publish session joins four facts:

### 1) Local source stays local-first

A publish session starts from a local service boundary:

- `bind_scope = loopback-only`, or
- `bind_scope = broker-held-loopback`

The service is still a local listener first.
The publish session does **not** silently convert that into ambient public listening.

### 2) Publication uses an explicit relay/transport path

The outward path is described by relay/transport evidence:

- `transport_policy_digest`
- `transport_receipt_digest`
- relay class / locator hints

This keeps provider-specific tunnels and relay stacks in the existing adapter discipline.
DeriveBSD standardizes the publication contract, not a specific SaaS, VPN mesh, or SSH workflow.

### 2.5) Published audience/publicness stays explicit

A publish session must also say **who the share is for** through
`published_endpoint.audience.class` plus `published_endpoint.audience.authn_mode`.
The archive now distinguishes audience-bound temporary sharing from explicit public exceptions:

- human preview/demo/support sharing should normally be `organization-users`, `named-recipients`, or `support-session-peer`,
- `public-webhook` is a separate callback posture rather than a human share default,
- and `public-link` is an explicit stronger exception, not the implied meaning of `internet`.

See `docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md`.

### 3) Authority stays explicit and bounded

A publish session must carry one of the recognized authority joins:

- `consent_receipt_digest`
- `policy_decision_digest`
- `operator_session_digest`
- `support_session_digest`

plus `lease_id` / `expires_at` so temporary publication cannot silently harden into standing
reachability. If the share is `support-peer`, that support-session join is no longer optional or inferred: the publish session must carry `authority.trigger = support-session` and the exact `authority.support_session_digest`.
The publish session must also declare lifecycle end conditions and stay reboot-cleared with `resume_policy = new-session-with-fresh-authority`, so relay tooling cannot quietly reappear after logout or reboot as a remembered tunnel. Public/org/support shares must also keep their locator posture `session-scoped`, so reserved relay domains, custom DNS, or remembered public hostnames do not become a backdoor durable-ingress story.
Secret-gated shares must also keep locator hints redacted: `url_hint` / `path_prefix` stay clean locator-only hints, any usable `single-use-secret` or `shared-secret` must travel through `published_endpoint.secret_handoff.secret_receipt_digest` rather than hiding in a query token, fragment, or pasted bearer URL, that separate handoff must stay `session-authority-bounded` so the secret cannot outlive the publish-session authority, and the handoff must also declare a consumption posture so `single-use-secret` means `single-successful-admission` while `shared-secret` stays `reusable-until-expiry`. The access-model posture is also now explicit: `public-link`, `public-webhook`, `organization-users`, and `named-recipients` stay `relay-url` shaped, `support-peer` stays `peer-relay` shaped instead of regressing to generic tunnel-URL folklore, and private `tailnet` sharing now stays `reverse-forward` shaped whenever the receipt says `tailnet-users`, `tailnet-identity`, or `tailnet-device-name`. Audience-bound receipts must now also carry the binding hints that make those labels explainable: `provider-identity` / `organization-users` shares name `identity_provider_hint`, and `named-recipients` shares name `recipient_hint`. Public callback publication must now carry `audience.validation_hint`, so `public-webhook` stops being URL-shaped-but-validation-hand-wavy. Endpoint hints now follow access model too: `relay-url` and `reverse-forward` shares carry `hostname + port`, only `relay-url` may carry `url_hint` / `path_prefix`, and `peer-relay` keeps URL/host endpoint hints absent. Relay-side locator grammar now follows access model as well: `relay.remote_locator.kind = uri-hint` stays in the `relay-url` lane, `peer-relay` uses `portal-object` or `opaque`, and `reverse-forward` uses `object-path` or `opaque`; see `docs/576-publish-session-relay-remote-locator-kind-follows-access-model.md`. Relay-side locator values now follow locator kind too: `relay.remote_locator.value` stays URI-shaped only for `uri-hint`, while `portal-object` / `object-path` / `opaque` values stay non-URI-shaped so support-session and tailnet lanes cannot smuggle URL-looking value text back in; see `docs/577-publish-session-relay-remote-locator-values-follow-locator-kind.md`.

### 4) Evidence stays summary-shaped

`net.publish.session` records the session envelope, endpoint hints, authority joins, transport
joins, and visible indicator state.
`net.listen.receipt` continues to say what listener state existed.
Per-connection traffic or full transcripts remain optional diagnostic/support artifacts rather
than baseline listener evidence.

## Product-shape posture

### A — fleet host

Use durable brokered service classes for real service publication.
Relay-backed publish sessions are exceptional support/breakglass tools, not the ordinary way to
put fleet services on the network.

### B — workstation

Relay-backed publish sessions are the **blessed ergonomic share path**.
They must be trusted-UI-visible, leased, revocable, easy to stop, and explicitly reboot-cleared.
The default human share should still stay audience-bound (`organization-users`, `named-recipients`,
or `support-session-peer`) rather than silently becoming a public bearer URL.
This is the archive's answer to preview URLs, webhook tests, and one-off demos without ambient
public listeners.

### C — general OS

Relay-backed publish sessions are also allowed for explicit admin/developer flows.
The compatibility escape hatch exists, but it stays bounded and receipted instead of normalizing
ambient tunnel daemons or folklore firewall edits.

### D — appliance factory / regulatory

Relay-backed publish sessions are not a production publication lane.
Any maintenance/lab use must remain exceptional and non-default; shipped/factory posture stays on
approved brokered services or offline/support workflows.

## What this deliberately does not decide

This boundary does **not** choose:

- a specific relay provider,
- a specific reverse-tunnel protocol,
- where TLS terminates in every adapter,
- or the exact UI/CLI for every B/C sharing flow.

Those remain adapter and implementation questions.
The archive only fixes the authority boundary, the lifetime boundary, the locator-posture boundary, the access-model posture boundary, the secret-handoff boundary, the secret lifetime-coupling boundary, the secret consumption posture boundary, and the evidence shape.

## Related docs

- `docs/286-inbound-listen-broker-and-firewall-leases.md`
- `docs/565-publish-session-session-scoped-locator-posture-boundary.md`
- `docs/566-publish-session-redacted-locators-and-separate-secret-handoff-boundary.md`
- `docs/567-publish-session-secret-handoff-lifetime-coupled-to-session-authority.md`
- `docs/568-publish-session-secret-consumption-semantics-boundary.md`
- `docs/570-publish-session-access-model-posture-boundary.md`
- `docs/571-publish-session-tailnet-reverse-forward-posture-boundary.md`
- `docs/572-publish-session-audience-bound-human-shares-stay-relay-url-shaped.md`
- `docs/574-publish-session-public-webhook-shares-require-validation-hints.md`
- `docs/575-publish-session-endpoint-hints-follow-access-model.md`
- `docs/576-publish-session-relay-remote-locator-kind-follows-access-model.md`
- `docs/460-inbound-listen-posture-by-profile.md`
- `docs/281-network-egress-broker-and-consent.md`
- `docs/255-policy-constrained-transports.md`
- `docs/291-remote-assistance-sessions-as-evidence.md`
- `docs/249-lease-registry-and-cross-lane-revocation.md`

Last updated: 2026-03-19r307