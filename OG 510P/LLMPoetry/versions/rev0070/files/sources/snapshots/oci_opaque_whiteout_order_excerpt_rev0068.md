# OCI Image Spec v1.1.1 opaque-whiteout and application-order semantics — bounded notes (rev0068)

Primary source: Open Container Initiative Image Specification v1.1.1, `layer.md`.
Accessed: 2026-06-18T13:00:00-04:00.
Evidence reference: `turn751730view0`.

Selected points used by P0004-D002:

- A whiteout applies to resources in lower or parent layers, not to files introduced by the layer containing the marker.
- The special empty file `.wh..wh..opq` marks its containing directory as opaque.
- An opaque marker hides all children of that directory from lower layers.
- The marker itself is not present in the resulting filesystem.
- Whiteout markers are applied before the other entries in the same layer, regardless of their order in the layer archive.

The last point is essential to D002: `appeal/status.txt` precedes the opaque marker in the upper tar yet survives, because the marker removes only pre-layer children before same-layer additions are applied.

This is a bounded paraphrase for traceability, not a complete copy of the specification and not literary evidence.
