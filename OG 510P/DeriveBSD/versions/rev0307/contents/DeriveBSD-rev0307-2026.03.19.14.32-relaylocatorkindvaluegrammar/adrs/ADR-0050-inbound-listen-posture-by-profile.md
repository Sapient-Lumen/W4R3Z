# ADR-0050: Inbound listen posture by profile

- Status: Accepted
- Date: 2026-03-06

## Context

DeriveBSD already has the building blocks for inbound exposure:

- listen classes and leases (`docs/286-inbound-listen-broker-and-firewall-leases.md`)
- PF anchor compilation (`docs/67-pf-anchors-per-instance.md`)
- socket/on-demand activation (`docs/238-portal-activated-services-and-socket-activation.md`)
- per-profile outbound-network posture (`adrs/ADR-0049-outbound-network-posture-by-profile.md`, `docs/459-outbound-network-posture-by-profile.md`)

But open question 17 still leaves the product shapes too fuzzy.
If inbound exposure stays “policy-defined in principle, details later,” the archive can quietly regress toward:

- workloads binding/listening directly and treating firewall state as a separate folk process,
- workstation apps casually becoming LAN/public services,
- “temporary” support/debug holes that are not leases or durable policy objects,
- and product shapes A/B/C/D converging on the least coherent default: ambient exposure.

We need a small, durable product-shape decision that keeps inbound exposure explicit without pretending to have solved every implementation detail.

## Decision

DeriveBSD adopts this baseline inbound-listen posture:

1. **Inbound exposure is a profile artifact, not ambient workload authority.**
2. **Loopback remains the low-friction default; broader exposure requires a brokered service class, a lease, or a durable policy object.**
3. **Interactive consent is only valid where a human is part of the product shape, and it must land in a lease or durable policy object.** A naked “open this port for now” click-path is not the stable policy surface.
4. **These defaults become part of the product profile artifact** (`spec/examples/product.profiles.json`) and are guarded by hygiene checks.

### Profile defaults

- **A (fleet_host):** `network_ingress=brokered-service-classes-noninteractive`
- **B (workstation):** `network_ingress=loopback-by-default-brokered-exceptions-with-lease`
- **C (general_os):** `network_ingress=brokered-service-classes-explicit-adapter-fallback`
- **D (appliance_factory):** `network_ingress=deny-by-default-offline-or-approved-brokered-service`

## Consequences

### What becomes true now

- Profile **A** keeps listener exposure policy-derived and non-interactive: services can be exposed, but not by ad-hoc approval on the host.
- Profile **B** gets a coherent workstation story: local developer tools may stay on loopback by default, while LAN/public exposure for general apps requires a trusted-UI-mediated lease or policy object.
- Profile **C** stays viable for dev/server use, but broader exposure remains explicit and reviewable rather than ambient.
- Profile **D** keeps regulatory/offline posture coherent: no prompt-driven support holes, only explicitly approved brokered services.

### What this ADR intentionally does **not** decide yet

This ADR does **not** settle:

- the final TLS termination / key-placement choices for every listener path,
- whether specific classes use FD passing vs proxy-forwarding vs broker-held sockets,
- the exact evidence budget for listener receipts vs per-connection telemetry,
- or the blessed developer/reverse-tunnel workflows for every edge case.

Those remain future RFC/ADR work.

## Why this is the smallest useful decision

This ADR does not invent a new subsystem.
It turns the archive’s existing listen-broker lessons into a **profile-true baseline**:

- loopback is easy,
- broader exposure is explicit,
- prompts only count where humans are part of the product shape,
- and prompts must land in leases/policy rather than folklore firewall edits.

That is enough to keep all four product shapes coherent while leaving implementation details open.

## Wiring

- Product profiles: `spec/examples/product.profiles.json`, `docs/411-product-profiles-as-compilation-target.md`, `docs/412-product-profile-matrix.md`
- Focused wiring doc: `docs/460-inbound-listen-posture-by-profile.md`
- Open questions / risk register: `docs/266-open-questions-and-risk-register.md`
- Related docs:
  - `docs/286-inbound-listen-broker-and-firewall-leases.md`
  - `docs/67-pf-anchors-per-instance.md`
  - `docs/238-portal-activated-services-and-socket-activation.md`
  - `docs/459-outbound-network-posture-by-profile.md`
