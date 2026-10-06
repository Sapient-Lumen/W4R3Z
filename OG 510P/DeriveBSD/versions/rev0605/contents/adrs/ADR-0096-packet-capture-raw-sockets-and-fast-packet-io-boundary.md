# ADR-0096: Packet capture, raw sockets, and fast packet I/O boundary

- Status: Accepted
- Date: 2026-03-08

## Context

`docs/459-outbound-network-posture-by-profile.md` now fixes ordinary outbound networking as a brokered,
profile-shaped authority lane, and `docs/505-network-learn-audit-convergence-contract.md` fixes learning as a
bounded evidence/review path rather than a standing permissive mode.

A quieter but more dangerous ambiguity remained:
what is the archive's default posture for **raw packet visibility and packet-path bypasses**?

If raw sockets, `/dev/bpf`, or fast packet I/O are treated as "just networking," several already-made decisions blur:

- DNS evidence posture can be bypassed by ambient packet capture,
- bounded learn sessions can collapse back into ad-hoc packet traces,
- workstation and fleet isolation stories degrade into "ops tooling gets host-wide visibility anyway,"
- and high-rate dataplane/acceleration features start sneaking in under ordinary app-networking review.

DeriveBSD needs a narrower answer than "networking is dangerous":
**raw packet visibility and fast-path packet I/O are a stronger authority lane than ordinary connect/listen.**

## Decision

1. Treat packet capture, raw sockets, and fast packet I/O as a **stronger network/device authority lane**,
   not as ordinary outbound-network authority.

2. Keep ordinary app/service networking on the existing governed lane:
   - `net-egress-policy` and brokered DNS mediation remain the normal authority surfaces,
   - `net-flow-receipt` / `net-dns-query-receipt` / `net-flow-summary` remain the explainability surfaces,
   - packet capture is not the baseline observability or learning workflow.

3. Treat `/dev/bpf`, raw sockets, and equivalent packet-tap/packet-injection facilities as **explicitly brokered or maintenance-scoped**:
   - never ambient for general workloads,
   - never silently implied by "can connect to the network",
   - and reviewed as both a networking change and a device-authority change.

4. Treat netmap/VALE and other fast packet I/O backends as a **default-off explicit acceleration/dataplane lane**.
   They are not an ergonomic compatibility escape hatch for ordinary applications.

5. Fix profile-shaped defaults:
   - **A:** bounded broker-owned capture is allowed for incident/canary/maintenance lanes; default-off reviewed acceleration only.
   - **B:** trusted-host bounded local capture is allowed for admins; ordinary apps do not receive raw sockets or ambient capture.
   - **C:** keep an explicit local-admin compatibility lane for legacy tools, but keep derived workloads on the stricter lane and keep acceleration/dataplane use explicit.
   - **D:** production defaults to none; only approved maintenance/lab lanes or purpose-built sealed dataplanes may use these features.

## Consequences

- `docs/201-network-egress-as-capability.md` can stop treating raw sockets / packet capture as an open question.
- `docs/303-flight-recorder-tracing-and-budgeted-diagnostics.md` can explicitly reject packet capture as the default evidence model.
- `docs/400-netgraph-and-netmap-as-derived-network-fabrics.md` can keep netmap/VALE as a deliberate backend/acceleration choice rather than a vague networking convenience.
- Device and network posture docs can point at the same fixed boundary instead of each implying half of it.
- A dedicated guardrail can keep future edits from quietly collapsing this lane back into "normal networking."

## Why this is narrow enough

This ADR does **not** standardize:

- exact broker UX for starting/stopping bounded capture sessions,
- exact retention/export schemas for captured packet material,
- exact raw-socket syscall filtering mechanics,
- exact netmap/VALE backend receipt shape,
- or exact capability names for every future fast-path primitive.

It only fixes the authority boundary so future schemas, docs, and code have a coherent target.
