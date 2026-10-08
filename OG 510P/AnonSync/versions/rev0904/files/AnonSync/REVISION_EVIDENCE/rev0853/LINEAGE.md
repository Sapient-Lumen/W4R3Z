# AnonSync rev0853 lineage

Rev0853 is derived only from the sealed canonical parent:

- parent revision: `rev0852`;
- parent archive: `AnonSync-rev0852-2026.07.19.21.01-typedpolicycapsule-constalias-compiletimebind-auditseal.zip`;
- parent archive SHA-256: `2a7492df93c4685686eeb99b153502a05d4c1986d60d12c8ee351111bb1e0753`;
- canonical archive root: `AnonSync/`;
- parent ZIP verification under the rev0853 verifier: **26/26**;
- extracted parent directory verification: **22/22**.

The rev0853 verifier adds
`src/persistence/sqlite_retained_callback_slots.hpp` to the revision-scoped
mandatory inventory. That requirement begins at rev0853, so the same verifier
continues to accept the sealed rev0852 parent.

`SOURCE_DIFF_rev0852_to_rev0853.patch` has SHA-256 `f2badc1ad59804edc136fedd712072b8396e62f63b0e47c0488360a8ab8f17e6`. It applies
cleanly to the verified rev0852 active tree. The replay tree matches the final
rev0853 active implementation on all **277/277** paths, with no missing file,
extra file, byte-count mismatch, or SHA-256 mismatch.

The final active implementation projection is
`f358327901848a6e026b3f2d3c798ecc20ad749e920d841702d2d441b2506586` over
**277 files / 17,640,630 bytes**.
