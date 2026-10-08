# OCI Image Spec v1.1.1 layout/manifest semantics — bounded notes (rev0067)

Primary sources: Open Container Initiative Image Specification v1.1.1, `image-layout.md` and `manifest.md`.
Accessed: 2026-06-18T11:12:00-04:00.
Evidence references: `turn770118view1`; `turn770118view2`.

Selected points used by P0004-D001:

- An OCI image layout contains `oci-layout`, `index.json`, and content-addressed blobs.
- Blob contents must match the digest encoded in their path and descriptor.
- An image manifest references one configuration object and an ordered layer list.
- The base layer is first, and subsequent layers are applied in stack order.
- The final filesystem must match the result of applying those layers to an empty directory.

This is a bounded paraphrase for traceability, not a complete copy of the specification and not literary evidence.
