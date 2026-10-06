# Slice evidence factor audit

Revision: rev0028

This audit asks whether a future session can find the evidence for the new persisted-spill slice without reading every file.

## Findings

- The manifest has a named slice: `ipc:persisted-spill-recovery-proof`.
- The slice writes a single JSON artifact: `REV0039-PERSISTED-SPILL-RECOVERY-PROBE.json`.
- The slice has a validation doc and an architecture frontier doc.
- The surface inventory names guarantees and non-claims.
- The impact map routes changes in implementation, probe, docs, manifest, and types to the right tasks.
- Browser artifacts are no longer secretly required by `check_cube.py` for a browser-light release.

## Remaining risk

The persisted-spill proof is semantic, not durable. Future sessions must not promote it to OPFS durability without a separate OPFS provider proof.
