# Network egress broker + consent (Little Snitch / OpenSnitch lesson)

Most “sandbox” designs fail the same way: the app can still talk to the network.
Outbound networking is frequently the *real* exfil channel, and “just use PF” often becomes folklore because:

- policy is scattered across `/etc`, service units, and tribal knowledge
- there’s no uniform story for *interactive* decisions ("this app wants to connect")
- incident response can’t easily answer **what left the system**

A greenfield OS can make outbound networking **lease-based, reviewable, and receipted**.

## Lessons to steal

- **Per-application outbound control** is a usable, mainstream concept (Little Snitch style).
- **Interactive prompts** are dangerous without a stable *policy landing spot* (users click Allow).
  Greenfield advantage: prompts should generate durable policy objects and default to short TTLs.
- **The enforcement plane should be boring**: compile to PF anchors + tables so the runtime isn’t a bespoke firewall.

## DeriveBSD mapping

### 1) Declare allowed egress as a named policy artifact

Define a host (or compartment) policy artifact that enumerates **egress classes**.
These are small, named shapes like:

- `dns-only`
- `https-anywhere`
- `ntp-secure`
- `registry:<vendor>`

Schema: `spec/net.egress.policy.schema.json`.

### 2) Promise profiles reference classes, not raw rules

Promise profiles should declare intent:

- `promises[]` includes `inet`
- `net.egress_classes[]` lists the named classes to request

Then the runtime/broker compiles those classes into concrete grants.

See: `docs/271-promise-profile-vocabulary-and-lint.md`, `docs/232-service-promise-profiles.md`.

### 3) Egress is granted as a lease, not ambient authority

The broker issues a signed, timeboxed grant:

- `net-egress-grant` (schema: `spec/net.egress.grant.schema.json`)
  - optional `lease_id`
  - constraints like `expires_at`, `max_flows`, and optional resource budgets

The grant is a first-class input to enforcement:

- PF anchor selection is derived from `{subject_digest, grant_digest}`
- PF tables contain the resolved CIDRs/ports allowed by the grant

### 4) Every flow produces evidence (bounded, redactable)

The broker (or a companion monitor) emits:

- `net-flow-receipt` (schema: `spec/net.flow.receipt.schema.json`)
  - which remote endpoints were attempted
  - allow/deny outcomes
  - optional byte counters
  - optional redaction transform digest

This makes “what connections happened?” answerable without packet-capture folklore.

### 5) Interactive consent is allowed, but must land in policy

When a workload without a matching egress class attempts a connection, the default should be:

- deny, emit a `net-flow-receipt` (`outcome=denied`)
- optionally offer an interactive consent surface (TTY/GUI)
  - if approved, create either:
    - a short-lived `net-egress-grant` (TTL minutes/hours), or
    - a proposed edit to `net-egress-policy` (reviewable, signed)

This is how you keep Little-Snitch-like UX from becoming “click-ops”.

## Where this plugs in

- PF anchor structure: `docs/67-pf-anchors-per-instance.md`, `adrs/ADR-0017-pf-anchors-unit.md`
- Inbound symmetry (listen is also a lease): `docs/286-inbound-listen-broker-and-firewall-leases.md`
- Workload identity + mTLS lane (optional): `docs/181-workload-identity-and-secretless-deploys.md`
- Runtime blast-radius / least authority: `docs/94-runtime-blast-radius-contract.md`, `docs/96-process-topology.md`
- Evidence spine: `docs/229-evidence-spine-overview.md`
- Export lane: exports should be explainable against egress receipts (`docs/251-export-policies-and-support-bundle-portal.md`)

Last updated: 2026-02-25
