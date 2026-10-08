# OCI Image Spec v1.1.1 layer/whiteout semantics — bounded notes (rev0067)

Primary source: Open Container Initiative Image Specification v1.1.1, `layer.md`.
Accessed: 2026-06-18T11:12:00-04:00.
Evidence reference: `turn770118view0`.

Selected points used by P0004-D001:

- Image layers serialize filesystem changesets, including removals.
- Removals are represented by whiteout file entries.
- A whiteout is an empty regular file whose name is `.wh.` plus the basename of the lower path to remove.
- Whiteouts apply only to lower or parent layers.
- After application, the whiteout marker itself is hidden.
- A layer tar must not contain duplicate entries for a file path.

This is a bounded paraphrase for traceability, not a complete copy of the specification and not literary evidence.
