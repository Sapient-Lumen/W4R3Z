# P0004-D001 OCI Whiteout and Release-Path Safety Audit — rev0067

## Substantive move

The cube was blocked on external reader evidence that it cannot manufacture. Rather than create another wrapper around that dependency or revise the frozen P0003 candidate, this revision opens a new machine-native wager: `P0004-D001`, **Must Also Be Hidden**.

The committed object is a deterministic OCI image layout. Its lower layer contains `appeal/objection.txt` with `I OBJECT TO THIS RECORD`. Its upper layer contains only the zero-byte whiteout `appeal/.wh.objection.txt`. Applying the layers removes the objection and hides the whiteout itself, while the manifest continues to reference both immutable content-addressed blobs. The page is ten nonblank body lines; the artifact carries the exact state transition.

## Primary artistic risk

The mechanism may produce a durable contradiction—deletion that remains structurally required—or it may be exhausted once a technically informed reader solves the whiteout rule. D001 is therefore same-turn unjudged and not a candidate. The later review must ask whether the objection survives as pressure after full disclosure, not merely whether the layout is valid.

## Concrete release defect found

The incoming rev0066 tree contained no symlinks and its archive was clean. However, `tools/build_manifest.py` and `tools/package_release.py` traversed regular-looking paths without rejecting symlinks. A later edit could therefore place a symlink inside the cube and cause bytes outside the cube root to be hashed or packaged under an apparently internal path. That is a provenance and containment failure, even if accidental.

## Refactor

The manifest builder and packager now reject symlinks, path traversal, absolute/backslash/control-character paths, and case-fold collisions. The packager reopens the completed zip and verifies the exact member set, member uniqueness, regular-file modes, fixed timestamps, and content hashes before emitting a SHA-256 sidecar. `tools/check_release_zip.py` exposes the same post-package inspection independently.

A synthetic symlink test is recorded in `reports/p0004_d001_oci_whiteout_release_path_safety_audit_rev0067.json`. The production tree remains symlink-free. The refactor does not add a new registry or change frozen poem bytes.

## Boundaries

- P0004-D001 is same-turn unjudged and not admitted, evidence-ready, or an anthology candidate.
- P0003-D004 remains byte-frozen as an internal candidate.
- P0002-D010's reader-response log remains empty.
- Local OCI conformance and safer packaging are not literary quality evidence.
