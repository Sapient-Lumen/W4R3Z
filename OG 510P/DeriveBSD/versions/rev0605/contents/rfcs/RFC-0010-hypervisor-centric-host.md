# RFC-0010: Hypervisor-centric DeriveBSD host model

- Status: draft
- Author(s): (add names)
- Created: 2026-02-23
- Last updated: 2026-02-23

## Summary
Make microVMs a first-class runtime in DeriveBSD, with a minimal host/control plane.

## Goals
- Define host vs workload trust boundaries
- Standardize microVM as an artifact target
- Define policy interfaces for VM lifecycle, networking, and secrets

## Non-goals
- Writing a new hypervisor
- Supporting every backend immediately

## Proposal
- Introduce a `derive-vmmd` control daemon that owns hypervisor privileges.
- MicroVMs are launched only from verified artifacts.
- Networking and firewall are managed via pf anchors generated from Spec/Plan.

## Open questions
- AuthN/AuthZ for VM lifecycle operations (local only vs remote API)
- Minimum observability that does not bloat the TCB
