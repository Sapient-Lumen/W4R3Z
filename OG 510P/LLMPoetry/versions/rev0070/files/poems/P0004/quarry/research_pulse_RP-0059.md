# RP-0059 — OCI whiteout, merged absence, and release-path safety

Official OCI Image Specification v1.1.1 material was used to verify whiteout naming, zero-byte representation, lower-layer scope, post-application hiding, layer order, and content-addressed layout semantics. The research entered P0004-D001 as a real deterministic OCI image layout, not as decorative container vocabulary.

A bounded release audit also found that the cube's packager and manifest builder would follow symlinks. Rev0067 changes them to reject symlinks, unsafe/case-colliding paths, and malformed output archives before a sidecar is issued. See `docs/40-audits/P0004_D001_OCI_WHITEOUT_RELEASE_PATH_SAFETY_AUDIT_rev0067.md`.

No quality, admission, reader-response, or publication claim follows from specification conformance.
