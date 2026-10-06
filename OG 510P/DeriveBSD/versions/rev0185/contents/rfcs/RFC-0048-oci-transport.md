# RFC-0048: Optional OCI transport for artifacts

- Status: draft
- Created: 2026-02-23

## Summary
Allow exporting/importing selected DeriveBSD targets via OCI Image + Distribution specs as a *transport*, without weakening DeriveBSD verification.

## Goals
- use registries as blob stores
- keep digests/signatures/attestations authoritative
- support airgap mirroring/export workflows

## References
- OCI image-spec, distribution-spec
