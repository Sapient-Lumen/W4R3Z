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
- example: `spec/examples/net.publish.session.json` (`session_version = 0.33`)

A publish session joins four facts:

### 1) Local source stays local-first

A publish session starts from a local service boundary:

- `bind_scope = loopback-only`, or
- `bind_scope = broker-held-loopback`

The service is still a local listener first.
The publish session does **not** silently convert that into ambient public listening.
If `local_service.service_uri_hint` is present, it must also stay an absolute loopback-shaped URI with no userinfo, query, or fragment so the local source hint cannot quietly point at a LAN/public target or become a localhost credential string; see `docs/580-publish-session-local-service-uri-hints-stay-loopback-shaped.md`.

### 2) Publication uses an explicit relay/transport path

The outward path is described by relay/transport evidence:

- `transport_policy_digest`
- `transport_receipt_digest`
- relay class / locator hints

This keeps provider-specific tunnels and relay stacks in the existing adapter discipline.
DeriveBSD standardizes the publication contract, not a specific SaaS, VPN mesh, or SSH workflow.
If `published_endpoint.hostname` is present, it must also stay a lowercase host-shaped token instead of a pasted URL, `host:port`, or localhost-style name, so the canonical host half of the published endpoint stays typed and non-local; see `docs/581-publish-session-published-endpoint-hostnames-stay-host-shaped.md`.
If the published endpoint also carries `url_hint` / `path_prefix`, those hints now have to serialize the
same `hostname + port + path_prefix` tuple inside the `relay-url` lane, `published_endpoint.path_prefix` itself now also stays normalized and URI-path-safe so the typed path cannot smuggle repeated separators, dot-segment folklore, percent-encoding, raw spaces, or backslashes, and the outward `url_hint` now also stays https-shaped with no userinfo so the copyable URL surface keeps the same secure relay/public-callback story as the typed tuple; see `docs/579-publish-session-url-hints-follow-endpoint-tuple.md`, `docs/582-publish-session-path-prefixes-stay-normalized.md`, `docs/585-publish-session-path-prefixes-stay-uri-path-safe.md`, and `docs/583-publish-session-relay-url-hints-stay-https-shaped.md`.

### 2.5) Published audience/publicness stays explicit

A publish session must also say **who the share is for** through
`published_endpoint.audience.class` plus `published_endpoint.audience.authn_mode`.
The archive now distinguishes audience-bound temporary sharing from explicit public exceptions:

- human preview/demo/support sharing should normally be `organization-users`, `named-recipients`, or `support-session-peer`,
- `public-webhook` is a separate callback posture rather than a human share default,
- and `public-link` is an explicit stronger exception, not the implied meaning of `internet`.

See `docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md`.

### 3) Authority stays explicit and bounded

A publish session must carry an authority join: authority joins now follow `authority.trigger` exactly:

- `trusted-ui` → `consent_receipt_digest`
- `policy` → `policy_decision_digest`
- `operator-session` → `operator_session_digest`
- `support-session` → `support_session_digest`

plus required `lease_id` / `expires_at` so temporary publication cannot silently harden into standing
reachability or become hard to revoke/query as a real lease-shaped share instance. Mixed authority-digest lanes are now out of bounds in the same receipt, so support/UI/export do not have to guess whether a share was “really” a consent lane, a policy lane, an operator-session lane, or a support-session lane; every publish session now also stays lease-addressable through `authority.lease_id`; and maintenance stays reserved and digest-empty until a dedicated maintenance-window join exists instead of borrowing one of those other digest families as placeholder proof; see `docs/586-publish-session-authority-joins-follow-trigger.md`, `docs/587-publish-session-authority-stays-lease-addressable.md`, and `docs/590-publish-session-maintenance-triggers-stay-digest-empty.md`. If the share is `support-peer`, that support-session join is no longer optional or inferred: the publish session must carry `authority.trigger = support-session` and the exact `authority.support_session_digest`. That support-session trigger itself now also stays support-peer shaped, so support proof cannot justify a public callback/demo or ordinary audience-bound `relay-url` share; see `docs/588-publish-session-support-session-triggers-stay-support-peer-shaped.md`.
The publish session must also declare lifecycle end conditions, stay reboot-cleared with `resume_policy = new-session-with-fresh-authority`, keep `lifecycle.post_end_access_posture = explicit-ended-or-fresh-share`, keep `lifecycle.post_end_access_posture = explicit-ended-or-fresh-share`, keep `lifecycle.post_end_management_return_posture = exact-ended-state-if-followed`, and preserve `lifecycle.terminal_end_condition` whenever `ended_at` is present, so relay tooling cannot quietly reappear after logout or reboot as a remembered tunnel, stale copied/bookmarked/share handles cannot silently land on a successor session, a generic launcher, or a durable ingress surface after the bounded share ends, any surviving trusted-UI return path or management deep link that is followed after end must still land on the explicit ended state for that same lease instead of a generic share home, a successor lease, or a blank miss, and the explicit ended bounded-share state itself does not have to flatten lease expiry, manual revoke, local-service loss, session end, or host reboot into a vague terminal label; see `docs/598-publish-session-post-end-access-stays-fail-closed.md`, `docs/602-publish-session-post-end-management-return-stays-lease-exact-ended.md`, and `docs/603-publish-session-ended-states-stay-terminal-cause-exact.md`. Public/org/support shares must also keep their locator posture `session-scoped`, so reserved relay domains, custom DNS, or remembered public hostnames do not become a backdoor durable-ingress story.
Secret-gated shares must also keep locator hints redacted: `url_hint` / `path_prefix` stay clean locator-only hints, any usable `single-use-secret` or `shared-secret` must travel through `published_endpoint.secret_handoff.secret_receipt_digest` rather than hiding in a query token, fragment, or pasted bearer URL, that separate handoff must stay `session-authority-bounded` so the secret cannot outlive the publish-session authority, the handoff must also declare a consumption posture so `single-use-secret` means `single-successful-admission` while `shared-secret` stays `reusable-until-expiry`, and `secret_handoff` now also follows `audience.authn_mode` exactly so non-secret lanes (`none`, `provider-identity`, `support-session`, `tailnet-identity`) keep it absent instead of carrying a second hidden secret story. The access-model posture is also now explicit: `public-link`, `public-webhook`, `organization-users`, and `named-recipients` stay `relay-url` shaped, `support-peer` stays `peer-relay` shaped instead of regressing to generic tunnel-URL folklore, and private `tailnet` sharing now stays `reverse-forward` shaped whenever the receipt says `tailnet-users`, `tailnet-identity`, or `tailnet-device-name`. Audience-bound receipts must now also carry the binding hints that make those labels explainable: `provider-identity` / `organization-users` shares name `identity_provider_hint`, and `named-recipients` shares name `recipient_hint`. `organization-users` now also stays organization-scoped, so the coworkers/IdP lane cannot quietly keep `exposure_scope = internet` while claiming to be audience-bound; see `docs/593-publish-session-organization-user-shares-stay-organization-scoped.md`. Those binding hints are inverse evidence too, so non-IdP lanes keep `identity_provider_hint` absent and non-recipient lanes keep `recipient_hint` absent instead of borrowing human-share binding prose as spare metadata; see `docs/592-publish-session-binding-hints-stay-lane-exact.md`. Public callback publication must now carry `audience.validation_hint`, and that `validation_hint` now also stays webhook-only, so `public-webhook` stops being URL-shaped-but-validation-hand-wavy without turning the same field into a generic spare note on public-link, human-share, or support-peer receipts; see `docs/591-publish-session-validation-hints-stay-webhook-only.md`. Endpoint hints now follow access model too: `relay-url` and `reverse-forward` shares carry `hostname + port`, only `relay-url` may carry `url_hint` / `path_prefix`, and `peer-relay` keeps URL/host endpoint hints absent. Inside the `relay-url` lane, `published_endpoint.path_prefix` now also stays normalized and URI-path-safe so the typed path cannot quietly carry repeated separators, `.` / `..` segments, percent-encoding, raw spaces, or backslashes while the URL hint claims to be canonical; see `docs/582-publish-session-path-prefixes-stay-normalized.md` and `docs/585-publish-session-path-prefixes-stay-uri-path-safe.md`. The outward published endpoint surface now also stays `lease-frozen`, so a later hostname/path/audience/access-model/exposure change mints a new `session_id` and `authority.lease_id` instead of silently repointing the same bounded share; see `docs/594-publish-session-published-endpoint-surface-stays-lease-frozen.md`. `published_endpoint.hostname` now also stays a lowercase host-shaped token, so the canonical host field itself cannot smuggle a URL, `host:port`, or localhost text back in; see `docs/581-publish-session-published-endpoint-hostnames-stay-host-shaped.md`. Relay-side locator grammar now follows access model as well: `relay.remote_locator.kind = uri-hint` stays in the `relay-url` lane, `peer-relay` uses `portal-object` or `opaque`, and `reverse-forward` uses `object-path` or `opaque`; see `docs/576-publish-session-relay-remote-locator-kind-follows-access-model.md`. Relay-side locator values now follow locator kind too: `relay.remote_locator.value` stays URI-shaped only for `uri-hint`, those same `uri-hint` values now also stay non-web-shaped so the relay-side locator cannot collapse into a second `http` / `https` public endpoint URL, and `portal-object` / `object-path` / `opaque` values stay non-URI-shaped so support-session and tailnet lanes cannot smuggle URL-looking value text back in; see `docs/577-publish-session-relay-remote-locator-values-follow-locator-kind.md` and `docs/584-publish-session-relay-uri-hint-locators-stay-non-web-shaped.md`. Optional relay-side `destination_hint` text now follows that same lane too: `uri-hint` shares keep `relay.destination_hint` identical to `relay.remote_locator.value`, while `portal-object` / `object-path` / `opaque` shares keep `destination_hint` non-URI-shaped so adjacent display text cannot reopen URL folklore; see `docs/578-publish-session-destination-hint-follows-remote-locator.md`.

### 4) Evidence stays summary-shaped

`net.publish.session` records the session envelope, endpoint hints, authority joins, transport
joins, and durable visible-indicator posture.
`net.listen.receipt` continues to say what listener state existed.
Per-connection traffic or full transcripts remain optional diagnostic/support artifacts rather
than baseline listener evidence.
The compact publish-session evidence object now also stays **baseline-envelope shaped**, **baseline-safe**, and **note-free**: it may
carry required typed `evidence.visible_indicator_posture = durable-until-ended`, `evidence.management_return_path_posture = trusted-ui-persistent-until-ended`, and `evidence.management_return_binding = lease-exact` plus the network receipt joins for the bounded share itself, but it no
longer carries `diagnostic_artifact_digests`, and commentary does not reappear as free-text `evidence.notes`. A one-shot toast or transient message is not enough to satisfy the active-share cue, a generic share home is not enough to satisfy the return path, and richer relay/admin/debug artifacts now belong on
`support.session`, `operator.session`, or `incident.bundle` joins instead of the baseline share
envelope; see `docs/595-publish-session-diagnostic-artifacts-stay-off-baseline-envelope.md`, `docs/596-publish-session-notes-stay-off-baseline-envelope.md`, `docs/597-publish-session-visible-indicators-stay-durable-until-ended.md`, `docs/600-publish-session-return-paths-stay-trusted-ui-persistent.md`, and `docs/601-publish-session-management-return-paths-stay-lease-exact.md`.

## Product-shape posture

### A — fleet host

Use durable brokered service classes for real service publication.
Relay-backed publish sessions are exceptional support/breakglass tools, not the ordinary way to
put fleet services on the network.

### B — workstation

Relay-backed publish sessions are the **blessed ergonomic share path**.
They must be trusted-UI-visible, leased, revocable, and explicitly reboot-cleared. Exact bounded-share evidence now requires `evidence.visible_indicator_posture = durable-until-ended` plus `evidence.revocation_affordance_posture = same-surface-durable-until-ended` plus `evidence.management_return_path_posture = trusted-ui-persistent-until-ended` plus `evidence.management_return_binding = lease-exact` plus `lifecycle.post_end_management_return_posture = exact-ended-state-if-followed`; and once `ended_at` is present, the bounded-share state should also preserve `lifecycle.terminal_end_condition`, so the live stop/revoke control stays on the same trusted UI surface as the active-share cue for the full session lifetime, that active-share surface stays reacquirable through a stable trusted-UI entry instead of hiding behind browser back/history luck, a one-shot toast, or route rediscovery, that return path lands back on the exact live bounded share rather than a generic share center or successor lease, any surviving post-end return path that is followed still resolves to the exact ended-share state for that same lease rather than dissolving into a generic share surface or blank miss, and the explicit ended state still keeps the exact bounded end-condition class instead of collapsing into `ended somehow`.
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
The archive only fixes the authority boundary, the lifetime boundary, the post-end access posture boundary, the locator-posture boundary, the access-model posture boundary, the secret-handoff boundary, the secret lifetime-coupling boundary, the secret consumption posture boundary, and the evidence shape.

## Related docs

- `docs/286-inbound-listen-broker-and-firewall-leases.md`
- `docs/565-publish-session-session-scoped-locator-posture-boundary.md`
- `docs/566-publish-session-redacted-locators-and-separate-secret-handoff-boundary.md`
- `docs/567-publish-session-secret-handoff-lifetime-coupled-to-session-authority.md`
- `docs/568-publish-session-secret-consumption-semantics-boundary.md`
- `docs/589-publish-session-secret-handoffs-follow-authn-mode.md`
- `docs/570-publish-session-access-model-posture-boundary.md`
- `docs/571-publish-session-tailnet-reverse-forward-posture-boundary.md`
- `docs/572-publish-session-audience-bound-human-shares-stay-relay-url-shaped.md`
- `docs/574-publish-session-public-webhook-shares-require-validation-hints.md`
- `docs/575-publish-session-endpoint-hints-follow-access-model.md`
- `docs/576-publish-session-relay-remote-locator-kind-follows-access-model.md`
- `docs/578-publish-session-destination-hint-follows-remote-locator.md`
- `docs/579-publish-session-url-hints-follow-endpoint-tuple.md`
- `docs/580-publish-session-local-service-uri-hints-stay-loopback-shaped.md`
- `docs/460-inbound-listen-posture-by-profile.md`
- `docs/281-network-egress-broker-and-consent.md`
- `docs/255-policy-constrained-transports.md`
- `docs/291-remote-assistance-sessions-as-evidence.md`
- `docs/249-lease-registry-and-cross-lane-revocation.md`
- `docs/599-publish-session-revocation-affordances-stay-same-surface-durable.md`
- `docs/600-publish-session-return-paths-stay-trusted-ui-persistent.md`
- `docs/601-publish-session-management-return-paths-stay-lease-exact.md`

Last updated: 2026-03-20r334

For the canonical current-stack map over the recent `docs/593-*` through `docs/603-*` tightening cluster, see `docs/604-publish-session-current-contract-stack-and-stale-entrypoint-firewall.md` rather than relying on this local page to act as the full companion list.

## Related

- `docs/604-publish-session-current-contract-stack-and-stale-entrypoint-firewall.md`
