# Inbound listen posture by profile

**Tier:** B (Cross-cutting product-shape decision)
**Profiles:** A, B, C, D
**Pillars:** isolation, operability
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate

Listening on a socket is one of the easiest ways for a system to drift from “derived and explainable” into “mysterious attack surface.”
Servers want published endpoints, workstations want local developer tools, general-purpose systems need pragmatic escape hatches, and regulatory deployments often want *no* listeners unless explicitly justified.

This doc records the smallest durable answer:

> inbound exposure is profile-shaped, not ambient, and loopback is the low-friction default while broader exposure must land in brokered classes, leases, or durable policy.

See `adrs/ADR-0050-inbound-listen-posture-by-profile.md`.

## Baseline rule

Across all profiles:

- workloads do **not** receive ambient “bind/listen and poke the firewall until it works” authority as the design baseline,
- loopback remains the easy local default,
- non-loopback exposure is governed through brokered service classes, leases, or durable policy objects,
- deny/explain is a first-class outcome,
- and any interactive approval must produce a short-lived lease or a durable policy edit that can later be reviewed and revoked.

This keeps inbound exposure aligned with the archive’s wider model: authority is explicit, bounded, and evidenced.

## Profile defaults

| Profile | `network_ingress` default | Practical meaning |
|---|---|---|
| **A fleet_host** | `brokered-service-classes-noninteractive` | Fleet/service listeners are exposed through policy-defined service classes and receipts, not ad-hoc host prompts; low-traffic admin surfaces should prefer on-demand activation when practical. |
| **B workstation** | `loopback-by-default-brokered-exceptions-with-lease` | General interactive apps may expose local loopback services by default, but LAN/public exposure requires a trusted-UI-mediated lease or durable policy object rather than ambient bind+firewall edits. |
| **C general_os** | `brokered-service-classes-explicit-adapter-fallback` | Derived workloads still prefer brokered listen classes, but legacy/dev workflows may use an explicit adapter fallback rather than forcing a fork or pretending every server workflow is broker-ready on day one. |
| **D appliance_factory** | `deny-by-default-offline-or-approved-brokered-service` | Regulatory/offline deployments default to no inbound exposure or tightly approved brokered services; interactive prompts are not the authority model. |

These values live in `spec/examples/product.profiles.json` and are guarded by `tools/check_product_profiles.py`.

## The hard decision hidden inside the table

The archive is now choosing **against** a universal “services can just open ports” mental model.
That means:

- profile **B** may support good trusted-UI prompts, but prompts are not the firewall database,
- profile **A** does not get dragged into workstation-style “temporary” exposure clicks,
- profile **D** does not pretend prompt-driven support holes are acceptable audit posture,
- and profile **C** gets its viability escape hatch explicitly, as an adapter-shaped fallback.

This is the same move made for egress and removable media:
**fallbacks may exist, but they must be named, bounded, and reviewable.**

## Loopback is special, but not ambient policy amnesia

Local-only developer tooling and helper services matter.
DeriveBSD’s baseline is to keep loopback easy *without* letting that turn into accidental LAN/public exposure.

So “run a local dev server” should normally remain a loopback action, while “share this service on the LAN / expose it remotely / open remote assistance” should become one of two explicit lanes:

1. a durable brokered service class / policy object when this is real host ingress,
2. or a **relay-backed publish session** (`net.publish.session`) when this is temporary sharing for B/C ergonomics.

Either way, the act stays leased or policy-derived, receipted, and reviewable.
For B/C temporary sharing, the relay-backed lane should also stay audience-bound by default (`organization-users`, `named-recipients`, or `support-session-peer`), reboot-cleared, `new-session-with-fresh-authority`, and `session-scoped` for public/org/support locators; `tailnet-device-name` is the only stable-name exception, `public-link` and `public-webhook` are explicit exception postures rather than the meaning of `internet`, authority joins now follow `authority.trigger` exactly too: trusted-UI shares carry `consent_receipt_digest`, policy shares carry `policy_decision_digest`, operator-session shares carry `operator_session_digest`, and support-peer publication carries the exact support-session authority join `authority.trigger = support-session` plus `authority.support_session_digest`, relay persistence or remembered hostnames must not become a stealth durable-ingress story, and secret-gated sessions must keep the locator redacted by joining any usable `single-use-secret` / `shared-secret` through `secret.receipt` rather than embedding it in the share URL while keeping the share secret lifetime inside the same session authority window and making the handoff consumption posture explicit so `single-use-secret` means `single-successful-admission` while `shared-secret` stays `reusable-until-expiry`. Private `tailnet` sharing should also stay `reverse-forward` shaped rather than speaking in public-share URL vocabulary, and audience-bound shares should now name the binding hints that make them explainable: `identity_provider_hint` for `provider-identity` / `organization-users`, and `recipient_hint` for `named-recipients`. Those binding hints are inverse evidence too, so non-IdP lanes keep `identity_provider_hint` absent and non-recipient lanes keep `recipient_hint` absent; `organization-users` now also stays organization-scoped, so the coworkers/IdP lane cannot quietly keep `exposure_scope = internet`; see `docs/593-publish-session-organization-user-shares-stay-organization-scoped.md` and `docs/592-publish-session-binding-hints-stay-lane-exact.md`. Public callback publication must now also carry `audience.validation_hint`, and that `validation_hint` now also stays webhook-only, so `public-webhook` stops being a URL-shaped callback with invisible verification posture without turning the same field into a generic note on non-webhook shares; see `docs/591-publish-session-validation-hints-stay-webhook-only.md`. Endpoint hints now follow access model too: `relay-url` and `reverse-forward` shares carry `hostname + port`, while `peer-relay` keeps URL/host endpoint hints absent. Relay-side locator grammar now follows access model as well: `relay.remote_locator.kind` stays `uri-hint` only for `relay-url`, stays `portal-object` / `opaque` for `peer-relay`, and stays `object-path` / `opaque` for `reverse-forward`. Relay-side locator values now follow locator kind too: `relay.remote_locator.value` stays URI-shaped only for `uri-hint`, those `uri-hint` values now also stay non-web-shaped so the relay-side locator does not collapse into a second `http` / `https` public endpoint URL, and `portal-object` / `object-path` / `opaque` values stay non-URI-shaped so support-session and tailnet lanes cannot hide URL-looking value text; see `docs/584-publish-session-relay-uri-hint-locators-stay-non-web-shaped.md`. Optional `relay.destination_hint` now follows that same split too: URL-shaped shares keep it identical to `relay.remote_locator.value`, while non-URI lanes keep it non-URI-shaped; see `docs/578-publish-session-destination-hint-follows-remote-locator.md`. Inside the `relay-url` lane, `url_hint` and `path_prefix` now also travel together and must serialize the same `hostname + port + path_prefix` tuple instead of drifting into a second URL surface; see `docs/579-publish-session-url-hints-follow-endpoint-tuple.md`. That outward published surface now also stays lease-frozen, so the same bounded share cannot quietly repoint hostname/path/audience/access posture under one lease; see `docs/594-publish-session-published-endpoint-surface-stays-lease-frozen.md`. The compact `net.publish.session` envelope now also stays baseline-safe, so richer relay/admin diagnostics move onto support/operator/incident evidence joins instead of `evidence.diagnostic_artifact_digests`; see `docs/595-publish-session-diagnostic-artifacts-stay-off-baseline-envelope.md`. That typed path half now also stays normalized and URI-path-safe, so `path_prefix` cannot quietly carry repeated separators, `.` / `..` segments, percent-encoding, raw spaces, or backslashes while the tuple claims to be canonical; see `docs/582-publish-session-path-prefixes-stay-normalized.md` and `docs/585-publish-session-path-prefixes-stay-uri-path-safe.md`. The canonical `published_endpoint.hostname` token now also stays lowercase + host-shaped rather than smuggling a pasted URL, `host:port`, or localhost text inside the same tuple; see `docs/581-publish-session-published-endpoint-hostnames-stay-host-shaped.md`. The outward `url_hint` in that same `relay-url` lane now also stays https-shaped with no userinfo instead of being an arbitrary absolute URI-shaped string; see `docs/583-publish-session-relay-url-hints-stay-https-shaped.md`. The local-source side must stay equally honest too: if `local_service.service_uri_hint` is present, it stays an absolute loopback-shaped URI with no userinfo/query/fragment so a supposedly local-first share cannot quietly point at a LAN/public target or hide localhost credentials; see `docs/580-publish-session-local-service-uri-hints-stay-loopback-shaped.md`. The authority lane must also stay singular and exact instead of mixing digest families, every publish session must also carry `authority.lease_id` so the bounded share instance itself stays directly revocable/queryable, a `support-session` trigger now also stays fully support-peer shaped instead of justifying non-support callback/demo or audience-bound URL shares, and non-secret authn modes now keep `secret_handoff` absent so provider-identity, support-session, tailnet-identity, or public-link lanes do not quietly grow a second hidden secret story; maintenance stays reserved and digest-empty too, so `authority.trigger = maintenance` cannot paste a maintenance label over borrowed consent/policy/operator/support proof while the dedicated maintenance lane is still unchosen; see `docs/586-publish-session-authority-joins-follow-trigger.md`, `docs/587-publish-session-authority-stays-lease-addressable.md`, `docs/588-publish-session-support-session-triggers-stay-support-peer-shaped.md`, `docs/589-publish-session-secret-handoffs-follow-authn-mode.md`, and `docs/590-publish-session-maintenance-triggers-stay-digest-empty.md`.
That keeps developer viability without normalizing invisible firewall folklore, shadow tunnels, remembered background shares, or copy-the-magic-URL secret handling. And once a bounded share ends, old copied/bookmarked/share handles now also stay fail-closed through `lifecycle.post_end_access_posture = explicit-ended-or-fresh-share` instead of silently dropping into a successor session or generic launcher.
See `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`, `docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md`, `docs/564-publish-session-end-conditions-and-no-auto-resume-posture-boundary.md`, `docs/565-publish-session-session-scoped-locator-posture-boundary.md`, `docs/566-publish-session-redacted-locators-and-separate-secret-handoff-boundary.md`, `docs/567-publish-session-secret-handoff-lifetime-coupled-to-session-authority.md`, `docs/568-publish-session-secret-consumption-semantics-boundary.md`, `docs/569-publish-session-support-peer-requires-support-session-authority-boundary.md`, `docs/570-publish-session-access-model-posture-boundary.md`, `docs/571-publish-session-tailnet-reverse-forward-posture-boundary.md`, `docs/572-publish-session-audience-bound-human-shares-stay-relay-url-shaped.md`, and `docs/574-publish-session-public-webhook-shares-require-validation-hints.md`, and `docs/576-publish-session-relay-remote-locator-kind-follows-access-model.md`. Public callback/demo publication stays `relay-url` shaped, support-peer sharing stays `peer-relay` shaped, and private tailnet sharing stays `reverse-forward` shaped.

## How this fits the workstation boundary

For profile **B**, this composes directly with `ADR-0047` and `ADR-0049`:

- the host remains trusted UI + brokers,
- general apps remain AppVM-first,
- network exposure is another mediated crossing like files/devices/clipboard,
- and both outbound and inbound networking now share the same contract: explicit authority, bounded duration, durable explanation.

That makes “this app wants to accept connections” structurally similar to “this app wants to connect out”: a brokered event, not ambient process power.

## How this fits A and D

### A) Fleet host

A fleet host should not normalize “someone clicked Open Port on prod.”
Its posture is:

- policy-derived service exposure,
- non-interactive by default,
- listener grants/receipts tied to the exposed workload,
- and topology changes handled through derived host networking plans.

### D) Appliance factory / regulatory

For regulated or air-gapped shapes, the right default is not to bolt on prompts.
It is to keep inbound exposure either absent or explicitly approved:

- support/inspection paths should be named and receipted,
- “temporary debug listeners” must not become invisible operational lore,
- and approved service exposure should remain stable enough for audit and factory documentation.

## What remains open

This doc does **not** settle:

- exact TLS termination / reverse-proxy patterns,
- whether a given class uses FD passing, proxy-forwarding, or broker-held sockets,
- evidence budget and retention for listener receipts vs per-connection logs,
- or every developer/remote-support workflow.

Those are narrower follow-on questions.

## Related docs

- `docs/286-inbound-listen-broker-and-firewall-leases.md`
- `docs/238-portal-activated-services-and-socket-activation.md`
- `docs/67-pf-anchors-per-instance.md`
- `docs/459-outbound-network-posture-by-profile.md`
- `docs/322-network-topology-and-firewall-as-derived-operations.md`

Last updated: 2026-03-20r328
