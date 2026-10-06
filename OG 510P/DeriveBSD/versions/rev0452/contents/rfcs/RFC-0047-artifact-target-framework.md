# RFC-0047: Unified artifact target framework

- Status: draft
- Created: 2026-02-23

## Summary
Define the shared target abstraction (target_kind, artifact_digest, runtime_manifest_digest, closure_digest, attestations) across host/microVM/unikernel/wasm.

## Goals
- reduce format sprawl
- keep backends pluggable but deterministic
- make targets policy-checkable and explainable

## References
- docs/73
