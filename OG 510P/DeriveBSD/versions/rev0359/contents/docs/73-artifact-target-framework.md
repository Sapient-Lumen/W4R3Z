# Artifact target framework (host, microVM, unikernel, Wasm)

DeriveBSD’s “Derive” pipeline should produce multiple **target kinds** behind one stable interface:

- **host**: ZFS boot-environment generation
- **microvm**: bhyve-first bundles
- **jail**: prebuilt jail roots (optional)
- **unikernel**: narrow high-assurance services (optional)
- **wasm**: capability-sandboxed WASI bundles (optional)

This document defines the shared “target” abstraction so we don’t grow Nix-like ad-hoc complexity.

## Target contract (v1)

A target is defined by:
- `target_kind` (enum)
- `artifact_digest` (content identity)
- `runtime_manifest_digest` (how it runs)
- `closure_digest` (what it depends on)
- `attestations[]` (provenance/SBOM/etc.)
- `policy_context_digest` (decision inputs)

## Target independence

- The store is target-agnostic: everything is objects + edges (docs/56).
- Target kinds differ only by:
  - their runtime mapping backend(s)
  - the manifest schema and validation rules
  - their deployment/activation mechanism

## Mapping layers

- **Spec/Lock/Plan → Artifact** (build)
- **Artifact + Policy → Runtime Manifest** (realize/run)
- **Manifest → Backend Config** (e.g., bhyve_config) (docs/40)

## Non-goals (v1)
- supporting “arbitrary user code” during evaluation (avoid hidden effects)
- making targets mutually incompatible “snowflake formats”

See RFC-0047 and ADR-0020.

Last updated: 2026-02-23
