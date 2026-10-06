# Outbound network posture by profile

**Tier:** B (Cross-cutting product-shape decision)
**Profiles:** A, B, C, D
**Pillars:** isolation, operability
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate

Networking is one of the easiest places for a multi-shape archive to become incoherent:
services want non-interactive automation, workstations want prompts, general-purpose systems need legacy escape hatches, and appliance/regulatory deployments often want offline operation first.

This doc records the smallest durable answer:

> outbound networking is profile-shaped, not ambient, and interactive consent only counts when it lands in a lease or durable policy surface.

See `adrs/ADR-0049-outbound-network-posture-by-profile.md`.

## Baseline rule

Across all profiles:

- general workloads do **not** receive ambient outbound authority as the design baseline,
- outbound connections are governed through brokered grants/policy classes,
- hostname-based policy implies brokered DNS mediation for that governed lane,
- deny/explain is a first-class outcome,
- and any interactive approval must produce either a short-lived lease or a durable policy edit that can later be reviewed and revoked.

This keeps outbound networking aligned with the archive’s wider model: authority is explicit, bounded, and evidenced.

A companion boundary is now fixed too: **raw packet visibility** (packet capture, raw sockets, fast packet I/O) is not ordinary outbound-network authority.
That stronger lane lives in `docs/506-packet-capture-raw-sockets-and-fast-packet-io-boundary.md`, which keeps app/service egress policy, DNS evidence posture, and packet-path authority from collapsing into one fuzzy network knob.

## Profile defaults

| Profile | `network_egress` default | `dns_resolution` default | Practical meaning |
|---|---|---|---|
| **A fleet_host** | `brokered-policy-derived-noninteractive` | `brokered-required-when-hostnames-appear` | Fleet/service egress is derived from policy and receipts, not GUI prompts; hostname rules require broker-owned resolution so incidents can reconstruct name→address decisions. |
| **B workstation** | `brokered-consent-with-durable-policy-landing` | `brokered-required` | General apps do not get ambient networking; user-facing prompts are allowed, but approval must become a lease or a reviewable policy object rather than a silent click-path. |
| **C general_os** | `brokered-by-default-explicit-adapter-fallback` | `brokered-preferred-explicit-fallback` | Derived workloads still prefer brokered egress, but legacy/dev workflows may use an explicit adapter fallback instead of forcing the project into a fork or pretending all software is portal-ready today. |
| **D appliance_factory** | `deny-by-default-offline-or-approved-brokered` | `brokered-or-none-fixed-policy` | Regulatory/offline deployments default to no network or tightly approved service egress; interactive prompts are not the authority model. |

These values live in `spec/examples/product.profiles.json` and are guarded by `tools/check_product_profiles.py`.

## The hard decision hidden inside the table

The archive is now choosing **against** a universal “networking is just there” mental model.
That means:

- profile **B** may have good prompts, but prompts are not the policy database,
- profile **A** does not get dragged into workstation-style click-ops,
- profile **D** does not pretend interactive consent is acceptable audit posture,
- and profile **C** gets its viability escape hatch explicitly, as an adapter-shaped fallback.

This is the same move made for removable media:
**fallbacks may exist, but they must be named, bounded, and reviewable.**

## DNS is part of the authority story

A lot of systems claim hostname-based egress policy but really enforce only an IP snapshot or a local resolver side effect.
DeriveBSD’s baseline is stricter:

- if a policy or prompt talks about a hostname,
- the broker resolves that hostname in the governed lane,
- the flow receipt can point at the DNS-query receipt,
- and name→address provenance remains explainable.

That does not mean every deployment must keep detailed DNS evidence forever.
It means the *authority boundary* owns resolution whenever names are the review surface.
The product-shape default for DNS receipt detail/export posture is now fixed in `docs/504-dns-receipt-detail-and-export-posture-by-profile.md`; exact windows/transforms remain implementation choices.
The learn/audit convergence contract is now fixed in `docs/505-network-learn-audit-convergence-contract.md`: `net-flow-summary` is the bounded review surface, and “observe first” is not allowed to become a standing ambient bypass.

## How this fits the workstation boundary

For profile **B**, this composes directly with `ADR-0047`:

- the host remains trusted UI + brokers,
- general apps remain AppVM-first,
- network access is another mediated crossing like files/devices/clipboard,
- and prompts must land in policy or leases rather than creating invisible exceptions.

So “this app wants to connect” should normally become:

1. broker denies/explains or asks via trusted UI,
2. approval creates a short TTL grant or a proposed policy change,
3. flows are receipted under that grant,
4. permission review UI can later explain/revoke what happened.

That is a smaller and more reviewable story than ambient `connect()` plus ad-hoc host firewall rules.

## How this fits A and D

### A) Fleet host

A fleet host should not normalize “someone clicked Allow on prod.”
Its posture is:

- policy-derived service egress,
- non-interactive by default,
- receipts for use/denial,
- and topology changes handled separately through derived host networking plans.

### D) Appliance factory / regulatory

For regulated or air-gapped shapes, the right default is not to bolt on prompts.
It is to keep egress either absent or explicitly approved:

- mirror kits and offline ingest are preferred,
- any online brokered service egress is narrow and policy-bound,
- DNS may be absent entirely or constrained to fixed brokered policy,
- and evidence exports can show that no hidden interactive lane existed.

## What remains open

The baseline is decided, but several implementation details remain open:

- exact retention windows and redaction-transform vocabulary for `net-flow-receipt` / `net-dns-query-receipt`,
- exact rendering/CLI ergonomics for bounded learn/audit sessions,
- and how explicit adapter fallback is rendered/reviewed in profile **C** without becoming ambient convenience.

Those belong in future RFC/ADR work, not in the baseline profile contract.

## Related docs

- `docs/411-product-profiles-as-compilation-target.md`
- `docs/412-product-profile-matrix.md`
- `docs/201-network-egress-as-capability.md`
- `docs/281-network-egress-broker-and-consent.md`
- `docs/305-dns-mediation-and-hostname-binding.md`
- `docs/322-network-topology-and-firewall-as-derived-operations.md`
- `docs/328-learned-network-policies-from-flow-receipts.md`
- `docs/369-consent-ledgers-and-permission-review-ui.md`

Last updated: 2026-03-08r235
