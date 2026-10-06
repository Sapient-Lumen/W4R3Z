# RFC-0090: Bootable host images over OCI (bootc lessons)

Status: Draft

## Summary

Define an optional import/export lane for DeriveBSD host generations as OCI artifacts.

This is inspired by the “bootable containers” ecosystem (bootc), but DeriveBSD preserves its
own trust + evidence rules.

References:
- bootc overview: https://bootc-dev.github.io/bootc/
- Fedora bootc docs: https://docs.fedoraproject.org/en-US/bootc/getting-started/

## Goals

- Reuse existing OCI registries as a distribution mechanism for host generations.
- Support mirroring/airgap workflows with minimal new tooling.
- Preserve DeriveBSD verification invariants (digest + signatures + attestations + policy).

## Non-goals

- Replacing ZFS boot environments as the primary atomic-switch mechanism.
- Adopting mutable package mutation semantics.

## Design sketch

- `derive export --oci host <generation>`
  - emits an OCI artifact with blobs representing a filesystem tree (or embedded ZFS stream)
  - includes a descriptor binding to plan digest, closure proof, and evidence refs
- `derive import --oci <ref>`
  - pulls, verifies, materializes into a ZFS BE, then performs health-gated activation

See: `docs/133-bootable-oci-host-images-bootc-lessons.md`.
