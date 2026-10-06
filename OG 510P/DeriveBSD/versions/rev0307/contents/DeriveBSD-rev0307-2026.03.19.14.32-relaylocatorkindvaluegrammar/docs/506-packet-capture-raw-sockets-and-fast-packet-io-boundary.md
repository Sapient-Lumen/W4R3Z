# Packet capture / raw sockets / fast packet I/O boundary

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate  

DeriveBSD already has a coherent story for ordinary governed outbound networking, DNS mediation, and bounded network-policy learning.
This doc fixes the next expensive boundary:
**raw packet visibility and fast packet I/O are a stronger authority lane than ordinary connect/listen.**

See also:
- ADR: `adrs/ADR-0096-packet-capture-raw-sockets-and-fast-packet-io-boundary.md`
- outbound-network baseline: `docs/459-outbound-network-posture-by-profile.md`
- network egress as capability: `docs/201-network-egress-as-capability.md`
- bounded learn/audit networking: `docs/505-network-learn-audit-convergence-contract.md`
- evidence posture: `docs/478-evidence-collection-posture-by-profile.md`
- device-authority posture: `docs/476-device-authority-posture-by-profile.md`
- packet-capture session/export contract: `docs/507-packet-capture-session-and-summary-first-export-boundary.md`
- netgraph/netmap lane: `docs/400-netgraph-and-netmap-as-derived-network-fabrics.md`

## Why this needs a hard decision

Without a fixed boundary, packet capture becomes the archive's silent escape hatch:

- DNS evidence promises degrade because host-wide packet visibility can bypass brokered resolution posture.
- Learn/audit sessions stop converging through bounded `net-flow-summary` review and fall back to ad-hoc packet traces.
- Workstation and fleet isolation stories quietly regain ambient cross-process visibility.
- netmap/VALE-like acceleration gets laundered in as "just networking" instead of remaining an explicit dataplane choice.

That is too much authority drift for a system that claims explicit capability and evidence boundaries.

## Accepted baseline

Across all profiles:

- ordinary app/service networking stays on the governed `net-egress-policy` lane,
- `net-flow-receipt`, `net-dns-query-receipt`, `net-flow-summary`, and `packet.capture.summary` remain the normal explainability surfaces,
- packet capture is **not** the baseline observability or policy-learning workflow,
- `/dev/bpf`, raw sockets, and equivalent packet-tap/packet-injection facilities are **never ambient** for general workloads,
- and netmap/VALE-style fast packet I/O stays **default off** and explicitly reviewed as an acceleration/dataplane lane.

This keeps evidence, enforcement, and high-authority packet access from collapsing into one fuzzy "network tooling" category.

## What belongs in this lane

The stronger lane includes:

- packet capture through `/dev/bpf`-like facilities,
- raw packet socket use / packet injection,
- whole-host or cross-compartment sniffing,
- fast packet I/O / zero-copy dataplane backends such as netmap/VALE,
- and purpose-built packet-processing components that bypass the normal brokered app-network model.

The key distinction is not implementation detail.
It is whether the subject gains **packet-path visibility or injection power** that exceeds ordinary reviewed connect/listen authority.

## What does **not** change

This doc does **not** replace the ordinary networking model:

- `net-egress-policy` remains the reviewed authority surface for ordinary outbound networking,
- hostname-based policy still relies on brokered DNS mediation where required,
- `net-flow-summary` remains the bounded learn/audit review surface,
- `packet.capture.summary` is the bounded packet-capture review/export surface,
- and flight-recorder / structured-diagnostics lanes remain the normal evidence UX for operability.

Packet capture may still exist, but as a stronger, explicit lane rather than a hidden prerequisite for routine troubleshooting.
When capture is allowed, the canonical session/export contract is `packet.capture.session` with summary-first export defaults (`docs/507-packet-capture-session-and-summary-first-export-boundary.md`).

## Product-shape defaults

| Profile | Default packet-capture / raw-socket posture | Default fast packet I/O posture | Practical meaning |
|---|---|---|---|
| **A fleet_host** | `broker-owned-bounded-incident-canary-maintenance-only` | `default-off-reviewed-acceleration-only` | Fleet hosts may capture when incident response or canary analysis truly needs it, but general services do not inherit raw packet authority. |
| **B workstation** | `trusted-host-bounded-local-capture-no-ambient-app-raw-sockets` | `default-off-admin-only` | Admins can do bounded local capture on the trusted host; ordinary apps still stay on mediated networking. |
| **C general_os** | `explicit-local-admin-compatibility-lane-derived-workloads-stay-strict` | `explicit-adapter-or-dataplane-lane` | General-purpose viability is preserved for legacy tooling, but compatibility is explicit and does not redefine the stricter default for derived workloads. |
| **D appliance_factory** | `production-none-approved-maintenance-or-lab-only` | `sealed-purpose-built-dataplane-only` | Regulated/sealed images should not quietly ship with ambient packet visibility or acceleration knobs enabled. |

## Review guidance

Treat proposals in this lane as **stronger than ordinary network-policy edits**.

Review should ask:

1. Is packet visibility/injection actually required, or would receipts/flow summaries/structured diagnostics solve the need?
2. Is the request bounded by incident, maintenance, lab, or trusted-host admin context?
3. Does the proposal widen both networking **and** device-authority posture?
4. Is netmap/VALE-style acceleration being introduced as a deliberate dataplane choice rather than a convenience escape hatch?
5. Does the resulting evidence/export posture remain coherent for the target profile?

These questions keep the archive honest about the difference between explainability and surveillance, and between ordinary connectivity and packet-path authority.

## Why this is worth locking now

This is a coherence cut, not a subsystem expansion.

It lets DeriveBSD keep all four product shapes viable without pretending they need the same answer:

- A keeps bounded incident-grade packet access without normalizing it for services,
- B preserves trusted-host troubleshooting without ambient app sniffing,
- C keeps compatibility viable without quietly weakening A/B/D,
- D gets a sealed production posture with explicit maintenance or dataplane exceptions only.

That is enough to guide future specs, broker design, and implementation work without freezing every backend detail.

Last updated: 2026-03-08r237
