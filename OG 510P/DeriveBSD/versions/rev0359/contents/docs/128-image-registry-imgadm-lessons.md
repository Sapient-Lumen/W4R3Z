# SmartOS-style image registries (imgadm/IMGAPI lessons)

SmartOS is a ZFS-first hypervisor OS that treats **images as first-class templates** for both Zones and VMs.
It relies on images “heavily”: images contain a disk/filesystem image **plus metadata**, and are managed with `imgadm`. (reference: https://docs.smartos.org/managing-images/)
The ecosystem also defines an **Image API (IMGAPI)** service that manages images alongside `imgadm`. (reference: https://images.smartos.org/docs/)

## What DeriveBSD should steal (conceptually)

- **Image = (bytes + metadata)**, not just bytes:
  - runtime requirements (machine type, virtio set, init system expectations)
  - declared injection interfaces (NoCloud ISO, virtio-9p, vsock agent, etc)
  - policy surface (needed capabilities)
  - provenance links (where derived from)

- **Image servers as boring infrastructure**:
  - list/lookup by digest + tags
  - upload/garbage-collect with policy
  - “promote from staging → stable” as an auditable action

## Mapping to DeriveBSD objects

- `Artifact` already covers “bytes”.
- Add/standardize a small `ImageDescriptor` schema:
  - references an Artifact digest
  - includes typed metadata for runtime + policy
  - is itself signed/attested

This keeps distribution flexible:
- OCI transport (layers) stays possible
- ZFS send streams stay possible
- plain “bundle tarball” stays possible

…but the *metadata contract* stays stable.

Related: `docs/24-microvm-artifact-target.md`, `docs/34-microvm-bundle-format.md`, `docs/73-artifact-target-framework.md`.

Last updated: 2026-02-23
