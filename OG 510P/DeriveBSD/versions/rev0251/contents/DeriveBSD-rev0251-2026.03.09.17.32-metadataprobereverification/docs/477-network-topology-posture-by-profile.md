# Network topology posture by profile

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Plan→Apply→Receipt, Broker→Lease→Receipt  

DeriveBSD already has typed network topology artifacts and brokered workload-facing networking.
What this doc decides is narrower and more important for coherence:
**how mutable is host networking by default in each product shape, and when do risky topology changes require maintenance, trusted UI, or commit-confirmed rollback?**

This is intentionally **not** a full Wi-Fi/VPN/network-manager spec.
It is a product-default decision.

See also:
- ADR: `adrs/ADR-0068-network-topology-posture-by-profile.md`
- host topology artifacts: `docs/322-network-topology-and-firewall-as-derived-operations.md`
- substrate mapping: `docs/64-networking-modes-mapping.md`
- egress broker: `docs/281-network-egress-broker-and-consent.md`
- listen broker: `docs/286-inbound-listen-broker-and-firewall-leases.md`
- authority budgets: `docs/298-authority-budgets-and-permission-drift-alarms.md`
- product profiles: `docs/411-product-profiles-as-compilation-target.md`

## Why this needs a hard decision

The archive already says networking should be planned, receipted, brokered, and rollbackable.
Without a profile-shaped default, those principles still drift in practice:

- fleet hosts accumulate incident-time `ifconfig`/route/`pf` folklore,
- workstation networking becomes either too opaque for humans or too casual for safe host mutation,
- general-purpose installs cannot tell whether derived networking is preferred or merely aspirational,
- and factory/regulatory systems claim sealed posture while still depending on ad-hoc live edits.

Networking posture is too foundational to leave as implied local custom.
The archive needs a stable default for **when topology mutation is activation-first, when it is trusted-UI-visible, and when commit-confirmed rollback is part of the baseline**.

## Scope of this knob

`networking` covers the default handling of:

- host link/address/route and `pf`-root mutation outside workload-facing egress/listen brokers
- whether risky topology changes are activation-first or can occur live
- whether commit-confirmed rollback is part of the default safety contract
- whether maintenance windows / leases / trusted UI are required for stronger host-topology mutation

It does **not** decide every Wi-Fi UX detail, route canonicalization rule, or firewall policy language.

## Product-shape defaults

| Profile | `networking` default | Practical meaning |
|---|---|---|
| A (`fleet_host`) | `activation-first-commit-confirmed-maintenance-leased` | Host topology is activation-first and policy-derived by default; risky live changes require maintenance leases and commit-confirmed rollback so remote-brick recovery stays real. |
| B (`workstation`) | `trusted-ui-local-first-commit-confirmed` | Ordinary local networking stays humane in the trusted UI, but risky host-topology changes must be visible, confirmable, and rollbackable rather than hidden shell folklore. |
| C (`general_os`) | `derived-preferred-explicit-admin-fallback` | Derived networking is preferred and receipted by default; explicit local-admin fallback remains viable for compatibility and lab workflows. |
| D (`appliance_factory`) | `sealed-offline-windowed-commit-confirmed` | Production topology is sealed by default; risky topology changes belong in approved maintenance windows with rollback or explicit confirmation, not ad-hoc live edits. |

These values live in `spec/examples/product.profiles.json` and are guarded by `tools/check_product_profiles.py`.

## Cross-profile invariants

Regardless of profile:

- host topology mutation must be **receipted** and explainable
- commit-confirmed / auto-revert semantics are preferred whenever a change can strand connectivity or silently broaden exposure
- workload-facing egress/listen brokers remain separate from host-substrate mutation
- `pf` root posture and anchor attachment points remain part of the topology review surface
- drift detection should describe the observed-vs-planned state without relying on shell history folklore

## What this fixes by profile

### A) Secure fleet host (`fleet_host`)

Default: `activation-first-commit-confirmed-maintenance-leased`

- Fleet hosts should not depend on heroic shell hotfixes to survive incidents.
- The default is activation-first host topology with maintenance-leased live mutation only when necessary.
- Commit-confirmed rollback is the baseline guardrail because remote bricks are not rare edge cases.

### B) Secure workstation (`workstation`)

Default: `trusted-ui-local-first-commit-confirmed`

- Users still need Wi-Fi, VPN, captive-portal, and local-link tasks to feel normal.
- The safety valve is not “hide networking behind policy servers”; it is trusted-UI visibility plus rollback for risky host-topology edits.
- This keeps workstation ergonomics real without normalizing invisible exposure-expanding changes.

### C) General-purpose OS (`general_os`)

Default: `derived-preferred-explicit-admin-fallback`

- General-purpose viability requires real local-admin escape hatches and lab-style experimentation.
- Derived networking remains the preferred path because it produces diffs, receipts, and predictable rollback.
- Compatibility fallback stays explicit rather than silently redefining stricter A/B/D defaults.

### D) Appliance factory / regulatory (`appliance_factory`)

Default: `sealed-offline-windowed-commit-confirmed`

- Production topology should not drift through hand-applied `ifconfig`/route/`pf` edits.
- Approved maintenance windows with rollback/confirmation are a better match for factory and regulatory environments than convenience shell access.
- Offline-capable maintenance matters more than assuming live upstream or central-network reachability at the moment of repair.

## What this does **not** decide yet

This doc does **not** freeze:

- the exact Wi-Fi/network-manager UX
- the exact confirm-window duration or health-check set
- the exact observed-topology canonicalization algorithm
- the exact split between `ifconfig`, `route`, `pfctl`, `if_bridge`, `netgraph`, and future adapters

Those remain implementation details or future RFC/ADR material.

## Why this is worth locking now

This decision collapses a recurring ambiguity without inventing a new subsystem:

- A gets activation-first, maintenance-leased, rollbackable topology mutation,
- B keeps humane local networking while making risky host edits trusted-UI-visible and confirmable,
- C keeps derived networking preferred without killing local-admin fallback,
- D gets a real sealed/maintenance-window production topology baseline.

That is enough to guide future specs and coding while keeping the topology planner, network UI, and backend adapters replaceable.

## Design cue from current systems

A few ecosystem lessons are durable:

- FreeBSD primitives are straightforward and powerful, but they historically leave persistence/audit as an exercise for the operator
- systemd-networkd demonstrates that links and addresses can be modeled as files rather than shell sessions
- Junos demonstrates that risky configuration changes should be confirmable with automatic rollback when management access might disappear
- OpenWrt demonstrates that even small-device systems benefit from “apply with automatic rollback unless confirmed”

DeriveBSD should steal those lessons while keeping topology planning, rollback policy, and maintenance authority explicit.

Last updated: 2026-03-06r207
