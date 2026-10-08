# Cloudtainer waste coherence refactor — rev0071

rev0071 separates four concepts that were becoming conflated.

| Concept | Correct home | Rule |
|---|---|---|
| Upstream source identity | source ZIP SHA256 + lane commits | Never depend on a local uploaded filename alone. |
| Historical audit trail | append-only docs/data | Preserve unless a compaction manifest proves safe removal. |
| Maintainer handoff | minimal packet bundle | Keep self-contained, but avoid copying whole cube evidence. |
| Current filing readiness | fresh current source + rerun matrix | Do not replace with archived-source gates. |

## Refactor decision

The cube should remain reviewable, but future revisions should stop copying large evidence tables into multiple trees. Exact duplicate groups should become pointer rows unless the file is part of a standalone clean-room export.

## Non-deletion boundary

rev0071 intentionally does not delete historical artifacts. Deletion without a manifest would trade disk waste for trust loss. The new gate makes future deletion reviewable by listing exact duplicates, sizes, hashes, and first paths.

## First compaction candidates for a later turn

1. Ranked audit queue snapshots: convert repeated full snapshots into one baseline plus deltas.
2. rev0064 source ZIP entry safety copies: keep canonical `data/` copy and turn duplicate `evidence/` copy into a pointer.
3. Manifest duplicates: keep canonical `manifests/` copy and remove repeated data mirror only after downstream helper references are checked.
4. Clean-room test duplicates: preserve only where needed for standalone export; otherwise use source-path pointers.
