# RFC-0023: Ecosystem integration adapters

Status: Draft

## Summary

Define adapter boundaries for integrating with existing tooling (vm-bhyve/libvirt/OCI tooling) without sacrificing DeriveBSD’s verification and policy semantics.

See `docs/43-ecosystem-integration.md`.

## Goals

- Allow external control-plane or image tooling as optional adapters.
- Keep verification/policy enforcement centralized.

## Non-goals

- Becoming a compatibility layer for every ecosystem.
