# ADR-0049: Outbound network posture by profile

- Status: Accepted
- Date: 2026-03-06

## Context

DeriveBSD already has good network building blocks:

- egress as a brokered capability (`docs/201-network-egress-as-capability.md`)
- egress policy/grants/receipts (`docs/281-network-egress-broker-and-consent.md`)
- DNS mediation and hostname binding (`docs/305-dns-mediation-and-hostname-binding.md`)
- host networking substrate as derived operations (`docs/322-network-topology-and-firewall-as-derived-operations.md`)
- learned network policy suggestions (`docs/328-learned-network-policies-from-flow-receipts.md`)

But open question 14 still leaves the product shapes too fuzzy.
If outbound networking stays “generally brokered, details later,” the archive can quietly regress toward:

- ambient direct-socket authority for convenience,
- GUI click-ops that do not land in durable policy,
- hostnames in policy without brokered DNS provenance,
- and profile **B** or **C** growing an implicit exception model that **A** and **D** cannot share.

We need a small, durable product-shape decision that keeps A–D coherent without pretending to have solved every enforcement and UX detail.

## Decision

DeriveBSD adopts this baseline outbound-network posture:

1. **Outbound networking is a profile artifact, not ambient default process authority.**
2. **Hostname-based policy implies brokered DNS mediation for the governed lane.** If policy speaks in hostnames, the broker owns resolution and records name→address provenance.
3. **Interactive consent is only valid where a human is part of the product shape, and it must land in a lease or durable policy object.** A naked “allow once” prompt is not the stable policy surface.
4. These defaults become part of the **product profile artifact** (`spec/examples/product.profiles.json`) and are guarded by hygiene checks.

### Profile defaults

- **A (fleet_host):** `network_egress=brokered-policy-derived-noninteractive`, `dns_resolution=brokered-required-when-hostnames-appear`
- **B (workstation):** `network_egress=brokered-consent-with-durable-policy-landing`, `dns_resolution=brokered-required`
- **C (general_os):** `network_egress=brokered-by-default-explicit-adapter-fallback`, `dns_resolution=brokered-preferred-explicit-fallback`
- **D (appliance_factory):** `network_egress=deny-by-default-offline-or-approved-brokered`, `dns_resolution=brokered-or-none-fixed-policy`

## Consequences

### What becomes true now

- Profile **A** keeps networking predictable and non-interactive: service/fleet egress is derived from policy, not prompt-driven.
- Profile **B** gets a coherent workstation story: apps do not receive ambient network authority, but interactive approval remains possible when it is captured as a short lease or a reviewable policy edit.
- Profile **C** stays viable for legacy and developer workflows, but the fallback is now explicit and adapter-shaped rather than silently ambient.
- Profile **D** keeps offline/regulatory posture coherent: deny by default, prefer mirror-kit/offline lanes, and allow brokered service egress only when policy explicitly says so.
- Hostname policy is no longer allowed to be “fake policy”; brokered DNS is part of the contract whenever names, rather than raw CIDRs, are the review surface.

### What this ADR intentionally does **not** decide yet

This ADR does **not** settle:

- the exact PF/vnet/backend enforcement mechanics for every protocol,
- the final redaction/retention defaults for flow and DNS receipts,
- the learn/audit workflow details for deriving candidate network policy,
- or how special cases like raw sockets and packet capture are surfaced in policy.

Those remain future RFC/ADR work.

## Why this is the smallest useful decision

This ADR does not invent a new subsystem.
It turns the archive’s existing networking lessons into a **profile-true baseline**:

- networking is brokered by default,
- human prompts are only for the human product shape,
- prompts must land in reviewable policy or short leases,
- and hostname-based policy must have brokered DNS evidence.

That is enough to keep all four product shapes coherent while leaving implementation details open.

## Wiring

- Product profiles: `spec/examples/product.profiles.json`, `docs/411-product-profiles-as-compilation-target.md`, `docs/412-product-profile-matrix.md`
- Focused wiring doc: `docs/459-outbound-network-posture-by-profile.md`
- Open questions / risk register: `docs/266-open-questions-and-risk-register.md`
- Related docs:
  - `docs/201-network-egress-as-capability.md`
  - `docs/281-network-egress-broker-and-consent.md`
  - `docs/305-dns-mediation-and-hostname-binding.md`
  - `docs/322-network-topology-and-firewall-as-derived-operations.md`
  - `docs/328-learned-network-policies-from-flow-receipts.md`
