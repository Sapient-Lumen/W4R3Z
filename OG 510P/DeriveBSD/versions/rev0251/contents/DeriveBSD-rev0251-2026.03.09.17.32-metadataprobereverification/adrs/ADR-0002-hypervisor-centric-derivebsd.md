# ADR-0002: DeriveBSD direction (hypervisor-centric)

- Status: proposed
- Date: 2026-02-23

## Context
DeriveBSD is intentionally FreeBSD-first. We want fast, real-world value while being “ridiculously secure from day 0”, and we want microVMs (bhyve) to be the default blast-radius boundary.

## Decision
Adopt **DeriveBSD** as the primary platform and evolve toward a **hypervisor-centric** runtime:
- jails for build isolation
- microVMs (bhyve-first) as the default runtime isolation boundary
- ZFS boot environments for host rollback
- ZFS-native image provisioning for microVM artifacts

## Consequences
- Standardize microVM artifact targets early (bundle + manifest + injection + policy).
- Keep the host control plane minimal and auditable.
- Future artifact targets (e.g., additional workload formats) may be added later if they preserve the FreeBSD-first security posture.
