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
For B/C temporary sharing, the relay-backed lane should also stay audience-bound by default (`organization-users`, `named-recipients`, or `support-session-peer`), reboot-cleared, `new-session-with-fresh-authority`, and `session-scoped` for public/org/support locators; `tailnet-device-name` is the only stable-name exception, `public-link` and `public-webhook` are explicit exception postures rather than the meaning of `internet`, support-peer publication must now carry the exact support-session authority join: `authority.trigger = support-session` plus the exact `authority.support_session_digest`, relay persistence or remembered hostnames must not become a stealth durable-ingress story, and secret-gated sessions must keep the locator redacted by joining any usable `single-use-secret` / `shared-secret` through `secret.receipt` rather than embedding it in the share URL while keeping the share secret lifetime inside the same session authority window and making the handoff consumption posture explicit so `single-use-secret` means `single-successful-admission` while `shared-secret` stays `reusable-until-expiry`. Private `tailnet` sharing should also stay `reverse-forward` shaped rather than speaking in public-share URL vocabulary, and audience-bound shares should now name the binding hints that make them explainable: `identity_provider_hint` for `provider-identity` / `organization-users`, and `recipient_hint` for `named-recipients`. Public callback publication must now also carry `audience.validation_hint`, so `public-webhook` stops being a URL-shaped callback with invisible verification posture. Endpoint hints now follow access model too: `relay-url` and `reverse-forward` shares carry `hostname + port`, while `peer-relay` keeps URL/host endpoint hints absent. Relay-side locator grammar now follows access model as well: `relay.remote_locator.kind` stays `uri-hint` only for `relay-url`, stays `portal-object` / `opaque` for `peer-relay`, and stays `object-path` / `opaque` for `reverse-forward`. Relay-side locator values now follow locator kind too: `relay.remote_locator.value` stays URI-shaped only for `uri-hint`, while `portal-object` / `object-path` / `opaque` values stay non-URI-shaped so support-session and tailnet lanes cannot hide URL-looking value text.
That keeps developer viability without normalizing invisible firewall folklore, shadow tunnels, remembered background shares, or copy-the-magic-URL secret handling.
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

Last updated: 2026-03-19r307