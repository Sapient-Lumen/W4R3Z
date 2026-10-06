# OCI as transport (optional): registry distribution for Derive artifacts

DeriveBSD does not want to become “containers 2.0”, but OCI specs are widely deployed as a *transport*:
- blob stores with dedup
- registries with auth
- standard tooling for mirroring

OCI Image spec defines manifests, configs, and layers.
OCI Distribution spec defines the registry API.

DeriveBSD can optionally package certain target kinds into OCI-compatible artifacts:
- microVM rootfs layers (filesystem tree or disk chunk layers)
- Wasm bundles
- metadata objects (attestations/SBOMs) as separate blobs referenced from an index

## Posture (v1)
- OCI support is optional; baseline caches can remain simple signed blob stores.
- If used, OCI must not weaken verification:
  - digest verification is mandatory
  - signatures/attestations remain DeriveBSD-native objects
  - optional: Sigstore/Cosign can be supported as an adapter evidence lane when publishing into registries (see docs/178-sigstore-keyless-signing-adapter.md)

## Why this matters
- enterprises already run OCI registries; adopting them reduces adoption friction
- distribution spec gives a stable API surface for replication and airgap export

## OCI for host OS generations (bootable containers / bootc lessons)

The “bootable containers” ecosystem (bootc) treats OCI images as a transport for transactional host OS updates.
DeriveBSD can adopt the transport idea without inheriting container-ecosystem assumptions.

References:
- bootc overview: https://bootc-dev.github.io/bootc/
- Fedora bootc docs: https://docs.fedoraproject.org/en-US/bootc/getting-started/

See: `docs/133-bootable-oci-host-images-bootc-lessons.md`.

## OCI beyond transport (optional): “microVM containers” (Kata lessons)

If DeriveBSD later wants a compatibility lane where an OCI workload can run inside a microVM, Kata Containers is the best prior art:
- it maps container lifecycle operations to a per-VM agent
- host↔guest control typically uses vsock

References:
- Kata design doc (virtualization mapping): https://github.com/kata-containers/kata-containers/blob/main/docs/design/virtualization.md
- AWS overview of Kata on Kubernetes (agent model): https://aws.amazon.com/blogs/containers/enhancing-kubernetes-workload-isolation-and-security-using-kata-containers/
- Kata blog note on microVM + vsock agent: https://katacontainers.io/blog/deploying-microvm-on-top-of-kubernetes/

See RFC-0048 and ADR-0021.
References in `docs/32-curated-references.md`.

Last updated: 2026-02-24
