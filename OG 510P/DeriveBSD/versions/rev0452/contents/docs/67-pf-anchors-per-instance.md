# pf anchors: per-instance firewall units (deterministic, auditable)

DeriveBSD’s networking story depends on **composable pf rules** that can be created/updated per microVM instance without rewriting the entire host ruleset.

pf supports **anchors**:
- `pf.conf(5)` describes anchor attachment points and optional parameterized anchors.
- `pfctl(8)` can load/replace rules in a named anchor, and list them.

(see `docs/32-curated-references.md`)

## DeriveBSD stance

This is the enforcement substrate for network brokers:
- outbound egress broker: `docs/281-network-egress-broker-and-consent.md`
- inbound listen broker: `docs/286-inbound-listen-broker-and-firewall-leases.md`

- The host maintains a small, stable “root pf ruleset” that contains:
  - global defaults (deny inbound, baseline anti-spoof)
  - an attachment point for Derive-managed anchors

- Each instance gets its own anchor:
  - `derive/inst/<instance_id>`
  - optional sub-anchors for directions: `in`, `out`, `nat`

## Lifecycle (v1)

- create: launch decides network mode → generates anchor rules → loads anchor
- update: replace anchor rules atomically (no partial state)
- delete: unload anchor + remove any tables created for that instance

Every step is logged with:
- instance_id
- manifest_digest
- policy decision digest
- pf_rules_digest

And, when composed into host networking changes, it is captured in `net.topology.receipt` as the anchor name + rules digest.

## Why anchors are key

- **blast-radius**: each instance firewall is isolated from others
- **reviewability**: rules are small diffs per instance
- **reproducibility**: same manifest + policy → same anchor rules
- **testability**: conformance tests can compare golden anchor output

## Non-goals (v1)

- complex dynamic rule generation at runtime beyond policy-allowed templates
- leaking host-global state into instance anchors

Last updated: 2026-02-26
