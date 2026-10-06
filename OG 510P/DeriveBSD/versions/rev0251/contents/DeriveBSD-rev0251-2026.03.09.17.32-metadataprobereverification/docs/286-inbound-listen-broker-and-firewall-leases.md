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

Last updated: 2026-03-06r189
