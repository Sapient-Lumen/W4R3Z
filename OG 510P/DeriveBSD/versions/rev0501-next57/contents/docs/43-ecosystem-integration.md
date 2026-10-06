# Ecosystem integration: vm-bhyve, libvirt, Sylve

DeriveBSD is not “a GUI hypervisor manager”. It is:
- a derivation pipeline + store
- a minimal host activation/rollback system
- a VM control plane (`derive-vmmd`) that launches verified artifacts under strict policy

## v1 stance
- Control plane remains `derive-vmmd` (ADR-0007).
- Existing managers (vm-bhyve/libvirt) are optional adapters (RFC-0023).
- We align with ecosystem primitives (virtio baseline, bhyve_config) to reduce friction.

## Why this matters
Interoperability helps adoption, but inheriting huge feature surfaces early destroys auditability.

Last updated: 2026-02-23
