# Bootable host images over OCI (bootc lessons)

DeriveBSD is ZFS-generation-native and microVM-first, but it can still benefit from the
growing ecosystem around **bootable containers**: using OCI images as a transport for
*host OS filesystem trees* with transactional updates.

Upstream “bootc” is explicitly about transactional, in-place OS updates using OCI images.

References:
- bootc project overview: https://bootc-dev.github.io/bootc/
- CNCF project page (context/status): https://www.cncf.io/projects/bootc/
- Fedora docs: Getting started with bootable containers: https://docs.fedoraproject.org/en-US/bootc/getting-started/
- Update-size optimization note (layer isolation): https://developers.redhat.com/articles/2025/11/03/reduce-bootc-system-update-size

## Why this matters to DeriveBSD

OCI registries are everywhere.
If DeriveBSD can **import/export host generations as OCI artifacts**, it gains:
- easier mirroring and airgap workflows
- reuse of existing registry auth/audit infrastructure
- a compatibility lane for orgs that already “GitOps” their base OS as an image

This does *not* mean adopting a container-style layering model as our internal representation.
It’s transport.

## DeriveBSD mapping (conceptual)

DeriveBSD already has:
- a Plan digest
- an Artifact digest
- ZFS boot environments for atomic switching

An OCI “host image” export can be:
- one or more blobs representing a filesystem tree (or a ZFS send stream embedded as a blob)
- a config/descriptor JSON that binds the tree to:
  - plan digest
  - closure proof
  - provenance/SBOM references
  - required policy decision record digest

### Import flow (sketch)

1) `derive import --oci <ref>` pulls blobs from a registry.
2) Verify digest + signature + required attestations (existing DeriveBSD rules).
3) Materialize into a ZFS dataset/BE (or decode a ZFS stream artifact).
4) Switch atomically and health-gate the new BE.

### Export flow (sketch)

1) `derive export --oci host <generation>` emits an OCI artifact.
2) Optional: attach attestations as OCI referrers.
3) Publish + transparency-log evidence as policy requires.

## Design guardrails

- OCI remains optional.
- OCI usage must not weaken verification: clients still verify digests/signatures/attestations.
- Avoid “mutable base via packages”; prefer whole-tree semantics (aligned with ZFS BEs).

See RFC-0090.

Last updated: 2026-02-26
