# ADR-0040: MicroVM orchestration is host-local (no distributed scheduler in v0)

- Status: **accepted**
- Date: 2026-03-04

## Context

Open question #4 in `docs/266-open-questions-and-risk-register.md` asks where the microVM boundary lives.

DeriveBSD needs a runtime isolation story that works for all product shapes (A–D) without forking:

- A (fleet host) needs to run many signed workloads, but must not grow a cluster scheduler inside the OS.
- B (workstation) needs AppVM-style isolation and ergonomic portals, but should keep the host control plane small.
- C (general OS) needs bounded compatibility lanes and dev UX, but cannot afford a "second Kubernetes".
- D (appliance/regulatory) needs sealed images, offline ops, and long-term rebuildability.

The archive already commits to:

- `derive-vmmd` as the enforcement boundary for microVM launches (ADR-0007).
- Adapter lanes for integration with external ecosystems (`docs/402-adapter-lanes-and-strangler-discipline.md`).
- Plan→Apply→Receipt as the operability spine for actions with security consequences.

If we treat microVM management as a cluster system, we risk building a scheduler, service discovery, networking policy stacks,
identity control planes, and state reconciliation machinery. This is the "build Kubernetes accidentally" failure mode.

## Decision

1) `derive-vmmd` is **host-local**.

- It owns *only* the local authority boundary: verifying workload artifacts, enforcing policy decisions, and emitting evidence.
- It is not a distributed scheduler, and it does not coordinate state across hosts.

2) Any distributed orchestration (fleet scheduling, reconciliation, service discovery) is **external**.

- External controllers may exist (Nomad/Kubernetes/custom), but they integrate via **adapter lanes** that:
  - submit digest-bound plans to each host,
  - consume host receipts/evidence as the source of truth,
  - remain killable and replaceable.

3) In v0, DeriveBSD does **not** standardize a cluster API.

- The stable contract is the *local* interface: plan inputs → policy decisions → receipts + evidence.
- Remote transport is an implementation detail (ssh, RPC, message bus) and must remain swappable.

## Consequences

- Scope stays coherent: DeriveBSD ships a strong enforcement + evidence boundary, not a scheduler.
- Product shapes remain compatible:
  - A can adopt external schedulers without compromising host verification/receipts.
  - B/C can run AppVMs and disposable microVMs locally.
  - D can run sealed workload images without introducing distributed state.
- Integration work becomes explicit:
  - "fleet orchestration" is an adapter lane with quarantine→promote, receipts, and reviewable diffs.
- We must keep the local surface excellent:
  - clear receipts, queryable evidence, and tight policy hooks are the value that external orchestrators should rely on.

## Alternatives considered

- **Ship a DeriveBSD-native scheduler/control plane.**
  - Rejected: too large; duplicates existing systems; risks becoming the real product.

- **Hard-bind to one external orchestrator.**
  - Rejected: violates the "no forks" goal and creates a hidden dependency that will drift across A–D.
