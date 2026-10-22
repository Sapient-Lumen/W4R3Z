# SlopOS collection: editions and provenance

[Collection entrance](README.md) · [Downloads](DOWNLOADS.md) · [Archive identities](ARCHIVES.json) · [Selected source identities](SOURCE-SELECTION.json)

This entrance brings together the 29 archives supplied by h0p3 on October 22, 2026: ten primary SlopOS editions and nineteen editions across Foundry, Harbor, Helm, Schell, Steward, ViewFS and Ward. The numbered snapshots are selected checkpoints, not a complete revision-by-revision history. The date-like strings in their names are retained artifact labels, not independently verified dates of authorship or execution.

## Preserve the works, explain the differences

All 29 complete ZIP archives are distributed byte-for-byte as supplied, with rev0800 reconstructed by concatenating its two supplied parts in order. The ZIP total is 118,947,598 bytes. Their internal files, paths, metadata, historical instructions and notices are not rewritten. GitHub normalizes the parentheses in the rev0183 asset name; the [archive manifest](ARCHIVES.json) records the supplied and downloadable names separately.

The browsing selection under `sources/` reproduces selected original file bytes. Only the outer archive-wrapper directory is omitted when present, so a readable path can identify project, revision and original relative path. [SOURCE-SELECTION.json](SOURCE-SELECTION.json) records each browsing path, original archive member, size, SHA-256 and Git executable mode. The selection is for direct reading, not a standalone build tree. Original documents may refer to other files available only in the complete ZIP, or to upstream work not included even there.

The rev0760 browsing files are recovered from the predecessor ZIP inside rev0800's `SlopOS/vault/source-archives/`. For these entries, the manifest's `member` identifies that nested ZIP, `nested_member` identifies the original file within it, and `nested_archive_sha256` fixes the intermediate archive's identity. They remain historical research and lineage material, not rev0800's active C++ build inputs.

The collection entrance, primary account, companion introductions and this reference layer are new editorial writing. They do not replace the originals or convert proposed contracts into implemented systems. Source-reading claims are distinguished from results recorded by the works; no newly executed SlopOS build, proof or usability study is claimed here.

## Related, not synchronized

h0p3 describes an uneven history of visibility: for most of the primary cube's life, its officers did not see the companion cubes, while the companions encountered the primary and one another in a scattered way. That supplied account is not evidence that every similar idea moved along a particular route.

The materials do show specific, directional references. ViewFS's [companion intake](sources/ViewFS/rev0176/docs/30-architecture/companion-seam-intake.md), Helm's [SlopOS seam map](sources/Helm/rev0221/docs/30-architecture/helm-slopos-seam-map-v0.md) and Foundry's [binding map](sources/Foundry/rev0103/docs/30-architecture/slopos-foundry-binding-map-v0.md) translate selected neighboring ideas into local design pressure. Such a reference establishes a local recorded relationship, not reciprocal reading or integrated runtime behavior. Each page therefore explains its own work before drawing connections.

The rev0800 primary archive also retains an important later contact point: its vault contains ZIPs byte-identical to all seven latest separately supplied companion editions, alongside an embedded SlopOS rev0760 archive. h0p3 subsequently clarified that the primary officer asked for the companions and was given them. That supplied account identifies a deliberate handoff; archive presence alone does not establish that every primary design adopted their proposals. The ten primary downloads count the separately supplied archives; the embedded predecessor remains inside rev0800.

## Attribution and notices

Original authorship statements and third-party notices remain in the full archives; selected source files retain their original contents. No new project-wide license is assigned by this presentation. In particular, rev0800's [LICENSE-NOTE.md](sources/SlopOS/rev0800/LICENSE-NOTE.md) explicitly does not assert a project-wide redistribution license and records its own proposed release gate. Its sealed-vault material remains included in the complete original ZIP, with the notices it carries; inclusion does not relicense it.

[W4R3Z preservation and rights](../../PRESERVATION.md) · [Owner-supplied legal notice](../../LEGAL-NOTICE.txt)
