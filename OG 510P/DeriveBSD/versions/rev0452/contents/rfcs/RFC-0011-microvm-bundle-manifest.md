# RFC-0011: MicroVM artifact bundle and runtime manifest

- Status: draft
- Author(s): (add names)
- Created: 2026-02-23
- Last updated: 2026-02-23

## Summary
Define the microVM artifact bundle format, runtime manifest schema, and config/secrets injection contracts.

## Goals
- One portable definition realizable by multiple hypervisor backends
- Explicit, verifiable configuration
- No secret leakage into images

## Proposal (v1)
A microVM artifact contains:
- image payload (zvol/raw)
- runtime manifest (resources/devices/networks)
- config bundle (non-secret)
- signature + provenance metadata

## Open questions
- Standard virtio baseline across backends
- Migration strategy for stateful workloads
