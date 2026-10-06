# RFC-0070: CAS everywhere (action cache + CAS mental model)

- Status: draft
- Author(s):
- Created: 2026-02-23
- Last updated: 2026-02-23

## Summary

Extend the store model so that *all* derived objects are content-addressed and cacheable, not just final artifacts.

## Motivation

Nix’s binary cache is powerful, but other build systems have a clearer architecture:
- **Action cache**: map action key → action result
- **CAS**: store blobs/trees by digest

This enables:
- high reuse
- remote builders
- verification by recomputation

## Goals / Non-goals

Goals:
- Plan digest is the primary “action key”
- action result points at CAS digests for outputs
- unify caching of proofs, SBOMs, attestations, logs

Non-goals:
- requiring remote execution

## Proposal

- Keep the existing content-addressed store as the CAS.
- Introduce an “action result” object keyed by Plan digest:
  - points at output digests (artifact, closure manifest/proof, SBOM, attestations)
  - records toolchain digest and sandbox policy digest

- Cache servers replicate CAS objects with signed metadata and policy constraints.

## Alternatives considered

- treat intermediate objects as “implementation detail” (harder verification)

## Backwards compatibility

- existing artifacts remain valid; new objects are additive.

## Security considerations

- treat cache as hostile; all objects verified by digest + signature
- consider making action cache read-only in shared infra

## Open questions

- do we need separate namespaces for “build logs” and “artifacts”?
- retention policy for CAS objects
