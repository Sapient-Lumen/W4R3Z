# Inbound listen broker + firewall leases (socket activation / inetd lesson)

Listening on a network socket is **authority**:

- it exposes an attack surface
- it creates an externally-reachable identity (“this machine speaks on port X”)
- it silently mutates firewall state in practice (people open holes until it works)

Most systems treat this as ambient power: daemons bind ports directly and operators separately edit firewall rules.
A greenfield OS can do better: make inbound exposure **policy-defined, lease-based, and receipted**.

## Lessons to steal

- **Socket activation** (inetd/systemd) proves you can separate “own the socket” from “run the service”.
- **PF anchors** prove you can keep enforcement boring and modular while still being dynamic.

Greenfield advantage: unify both into a single lane with evidence objects.

Product-shape default now lives in `adrs/ADR-0050-inbound-listen-posture-by-profile.md` and `docs/460-inbound-listen-posture-by-profile.md`: loopback is the low-friction default, broader exposure is brokered/leased/policy-defined, and only human-shaped products may use trusted-UI consent for non-local exposure.

## DeriveBSD mapping

### 1) Define listen classes as a signed policy artifact

A `net-listen-policy` enumerates small, named classes that describe what a service may expose.
Examples:

- `loopback-http` (127.0.0.1/::1 only)
- `lan-ssh` (RFC1918 + VPN ranges)
- `public-https` (WAN, tcp/443)

Schema: `spec/net.listen.policy.schema.json`.

### 2) Promise profiles reference classes, not raw sockets

Promise profiles should declare *intent*:

- `promises[]` includes `inet-listen`
- `net.listen_classes[]` lists allowed listen classes

Lints should reject:

- services that bind/listen without a matching class
- “wildcard listen” classes outside explicit breakglass contexts

See: `docs/232-service-promise-profiles.md`, `docs/271-promise-profile-vocabulary-and-lint.md`.

### 3) The broker owns the listening socket and the firewall hole

A privileged **listen broker**:

- binds the socket (or selects from a pre-bound pool)
- compiles the class → PF anchor rules
- optionally uses socket-activation semantics (spawn on demand, pass FD)
- emits a **grant** and a **receipt**

Evidence objects:

- `net-listen-grant` (schema: `spec/net.listen.grant.schema.json`)
- `net-listen-receipt` (schema: `spec/net.listen.receipt.schema.json`)

Operationally:

- firewall rules are always derived from `{subject_digest, grant_digest}`
- PF anchors/tables are the only enforcement plane
- grants are timeboxed by default (TTL hours/days), with explicit “permanent” policy edits when warranted


### 3.5) Temporary sharing is a relay-backed publish session, not a casual public listener

For demos, webhook tests, and short support handoffs, the blessed path is now `net.publish.session`:
keep the service local-first (`loopback-only` or `broker-held-loopback`), publish it through an approved relay/transport path, and bind the act to expiry + authority evidence instead of teaching users to open a public port or run a shadow tunnel.

That lane is no longer allowed to leave audience/publicness implicit. The publish session must say whether it is audience-bound (`organization-users`, `named-recipients`, `support-session-peer`, `tailnet-users`) or one of the explicit public exceptions (`public-webhook`, `public-link`). `public-webhook` shares must now also carry `audience.validation_hint`, so callback publication names the verification posture instead of leaving it in adapter folklore. For support-peer publication, the support-session authority lane must now stay exact too: `authority.trigger = support-session` plus `authority.support_session_digest`, rather than a generic share wearing support language.
In other words: **temporary sharing** uses the separate relay-backed publish-session lane instead of turning ad-hoc public listeners into the real workflow, the normal B/C path stays audience-bound rather than silently becoming a public-link, the public/org/support locator stays `session-scoped` rather than moving onto reserved relay domains or remembered public hostnames, the session itself stays reboot-cleared with `resume_policy = new-session-with-fresh-authority` instead of hiding a restart-persistent tunnel inside relay tooling, and secret-gated sessions keep the locator redacted by joining any usable secret through `secret.receipt` rather than embedding it in a bearer URL while also keeping that secret lifetime inside the same session authority window and making the handoff consumption posture explicit so `single-use-secret` means `single-successful-admission` while `shared-secret` stays `reusable-until-expiry`. Public callback/demo sharing stays `relay-url` shaped, `organization-users` / `named-recipients` human shares also stay `relay-url` shaped, support-peer sharing stays `peer-relay` shaped, and private tailnet sharing stays `reverse-forward` shaped. Audience-bound shares must now also carry the exact binding hints that make those labels real: `identity_provider_hint` for `provider-identity` / `organization-users`, and `recipient_hint` for `named-recipients`. Public callback publication must now also carry `validation_hint`, so `public-webhook` no longer reads as a callback URL with invisible receiver-side verification. Endpoint hints now follow access model too: `relay-url` and `reverse-forward` shares carry `hostname + port`, while `peer-relay` keeps URL/host endpoint hints absent. Relay-side locator grammar now follows access model as well: `relay.remote_locator.kind` stays `uri-hint` only for `relay-url`, stays `portal-object` / `opaque` for `peer-relay`, and stays `object-path` / `opaque` for `reverse-forward`. Relay-side locator values now follow locator kind too: `relay.remote_locator.value` stays URI-shaped only for `uri-hint`, while `portal-object` / `object-path` / `opaque` values stay non-URI-shaped so support-session and tailnet lanes cannot hide URL-looking value text.
See `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`, `docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md`, `docs/564-publish-session-end-conditions-and-no-auto-resume-posture-boundary.md`, `docs/565-publish-session-session-scoped-locator-posture-boundary.md`, `docs/566-publish-session-redacted-locators-and-separate-secret-handoff-boundary.md`, `docs/567-publish-session-secret-handoff-lifetime-coupled-to-session-authority.md`, `docs/568-publish-session-secret-consumption-semantics-boundary.md`, `docs/569-publish-session-support-peer-requires-support-session-authority-boundary.md`, `docs/570-publish-session-access-model-posture-boundary.md`, `docs/571-publish-session-tailnet-reverse-forward-posture-boundary.md`, `docs/575-publish-session-endpoint-hints-follow-access-model.md`, and `spec/net.publish.session.schema.json`, and `docs/576-publish-session-relay-remote-locator-kind-follows-access-model.md`.

### 4) Bind/listen becomes explainable

Given a host at time T, `derive explain` should answer:

- which services were exposed
- which class/policy authorized each exposure
- the PF anchor/rules digest enforcing it
- whether exposure was interactive (consent) or pre-authorized

This mirrors the outbound lane’s “flow receipts”, but for the *act of exposure*.

### 5) On-demand activation is the default for low-traffic services

For services that don’t need to run continuously:

- the broker can hold the socket open
- spawn a fresh instance per connection (or per small batch)
- run each instance with tight promise profiles

This is the modernized “inetd” posture: reduce long-lived memory corruption risk and tighten forensic boundaries.

### 6) MicroVM integration

For workloads inside microVMs:

- the broker can terminate TLS / TCP on the host and forward via a constrained channel (e.g., vsock)
- or configure a per-VM PF anchor and pass the bound socket FD to the VM runner

The key invariant is the same: **no workload has ambient “open a port and poke the firewall” authority**.

## Where this plugs in

- PF anchor structure: `docs/67-pf-anchors-per-instance.md`, `adrs/ADR-0017-pf-anchors-unit.md`
- Socket activation / on-demand services: `docs/238-portal-activated-services-and-socket-activation.md`, `docs/196-capability-activation-and-escrow.md`
- Outbound networking lane (symmetry of “network authority as leases”): `docs/281-network-egress-broker-and-consent.md`
- Blast-radius diffs: `docs/106-blast-radius-diff.md`
- Evidence spine: `docs/229-evidence-spine-overview.md`

Last updated: 2026-03-19r307