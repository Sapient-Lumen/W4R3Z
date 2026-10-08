# OCI Image Spec v1.1.1 layout/manifest semantics — bounded refresh (rev0068)

Primary sources: Open Container Initiative Image Specification v1.1.1, `image-layout.md` and `manifest.md`.
Accessed: 2026-06-18T13:00:00-04:00.
Evidence references: `turn913736search3`; `turn913736search4`.

Selected points used by P0004-D002:

- An OCI image layout identifies content by descriptors and content-addressed blobs.
- An image manifest references the configuration and an ordered list of filesystem layers.
- Layer order is base-to-upper; the resulting filesystem is obtained by applying the listed changesets in that order.
- Descriptor digests and sizes bind the manifest to exact layer bytes.

P0004-D002 adds a stricter project-local closed-world contract: its blob directory may contain only the config, manifest, and two layer blobs reachable from `index.json`. That extra closure is an LLMPoetry verification rule, not a general claim that all OCI layouts forbid additional blobs.

This is a bounded paraphrase for traceability, not a complete copy of the specification and not literary evidence.
