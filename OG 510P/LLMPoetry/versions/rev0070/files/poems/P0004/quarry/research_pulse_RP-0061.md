# RP-0061 — candidate stop and contained OCI verification

D002 received a later-turn review against its exact rev0068 hashes. The review found that disclosure leaves a live contradiction: the merged filesystem says `NO APPEAL ON FILE`, while the manifest still requires the content-addressed lower layer containing the appeal records. D002 is frozen as an internal candidate rather than extended to D003.

The tooling audit found a separate high-severity latent flaw. Spec and descriptor components were not always proved canonical and contained before filesystem lookup or write. A shared fail-closed path module now guards both builder and checker, and temporary self-tests prove deterministic rebuilding plus rejection of traversal and symlink layouts.

No reader response or quality proof was created. See `docs/40-audits/P0004_D002_CANDIDATE_FREEZE_OCI_PATH_CONTAINMENT_AUDIT_rev0069.md`.
