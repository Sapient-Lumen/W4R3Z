# Bandwidth-efficient updates (static deltas as an optional lane)

DeriveBSD already has strong “whole-tree” transports:
- ZFS incremental send/recv
- OCI layer reuse
- CAS chunking (casync-like)

A recurring problem in atomic OS systems is that updates may involve **many small objects**, which can be network-inefficient.
OSTree addresses this with **static deltas**: precomputed delta artifacts between two commits that can also be applied offline.

References:
- OSTree “Static deltas for offline updates”: https://ostreedev.github.io/ostree/copying-deltas/
- RHEL for Edge note on static deltas: https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/composing_installing_and_managing_rhel_for_edge_images/creating-and-managing-ostree-image-updates_composing-installing-managing-rhel-for-edge-images

## Lesson to steal

- publish optional **delta artifacts** for common upgrade paths
- deltas can be **self-contained** (USB-friendly)
- clients can prefer deltas when available, otherwise fall back to full objects

## DeriveBSD mapping

### Delta artifacts are first-class Artifacts

- a delta is addressed and verified like anything else (digest + signature + policy)
- deltas must declare:
  - `from_generation_digest`
  - `to_generation_digest`
  - supported apply constraints (platform, ZFS feature flags, etc.)

### Multiple delta backends

- ZFS: incremental send streams
- CAS: chunkpack deltas (casync-like)
- OCI: layer/push deltas (where applicable)

### Layer-aware image construction (bootc / rpm-ostree lesson)

Even without explicit “delta artifacts”, update size can be dominated by *accidental invalidation*:
a tiny config change causes a huge blob to be re-downloaded because it shares a layer/chunk boundary.

Bootc/rpm-ostree work has highlighted a pragmatic mitigation: **isolate large, rarely-changing payloads**
into their own layers/chunks so small changes don’t force re-fetch of unrelated bytes.

Reference:
- Red Hat Developers: “Reduce bootc system update size” (layer isolation for large embedded payloads): https://developers.redhat.com/articles/2025/11/03/reduce-bootc-system-update-size

DeriveBSD mapping: treat “bundle construction” as an optimization lane:
- pack stable subtrees (models, firmware, large assets) into their own addressed objects
- make the packing strategy visible in receipts so “why was this update huge?” is answerable


### Why this matters

- improves rollout speed and reduces bandwidth without weakening verification semantics

Candidate RFC: *Delta artifact format + selection rules*.

Last updated: 2026-02-23
