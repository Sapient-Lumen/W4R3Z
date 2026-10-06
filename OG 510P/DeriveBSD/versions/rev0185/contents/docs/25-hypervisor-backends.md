# Hypervisor backends (bhyve-first, stable interface)

DeriveBSD defines a **hypervisor backend interface** and then implements backends.

## Backend capabilities
- start/stop/restart from an artifact bundle
- attach network and storage as described by manifest
- expose console/log channels
- report state for introspection/health
- optional confidential-computing flags (SEV-SNP/TDX/CCA) surfaced as capability bits and wired to receipts (`docs/330-confidential-microvms-and-tee-attestation-as-evidence.md`)

## Backends

### bhyve (FreeBSD-native)
- Aligns with BSD-host story
- Integrates well with ZFS datasets for image cloning

### Optional backends
- Firecracker / cloud-hypervisor for cloud parity (later)

## v1 stance
- **bhyve-first**
- Design interfaces so other backends can be added without changing Spec/Plan

## Control plane shape
Prefer a minimal privileged service:
- `derive-vmmd` owns hypervisor access
- CLI talks to daemon
- strong authorization on which identities can launch which artifacts


Last updated: 2026-02-23
