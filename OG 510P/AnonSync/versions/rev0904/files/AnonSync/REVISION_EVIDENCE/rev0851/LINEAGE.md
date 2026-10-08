# AnonSync rev0851 lineage

Rev0851 is derived only from the sealed canonical parent:

- parent revision: `rev0850`;
- parent archive: `AnonSync-rev0850-2026.07.19.18.32-authorizerlifefence-revokebeforeclose-auditdedupe-generationseal.zip`;
- parent archive SHA-256: `b2c0bf3b2b7d19c3234a80e331a9dd35fa8d6d5063e485cc66f1169664710ab4`;
- canonical archive root: `AnonSync/`;
- parent ZIP verification under the rev0851 verifier: **26/26**;
- extracted parent directory verification: **22/22**.

The newly mandatory owned-policy files are revision-scoped to rev0851 and later,
so the strengthened verifier continues to accept the sealed rev0850 parent.

`SOURCE_DIFF_rev0850_to_rev0851.patch` has SHA-256 `8800bbe70d6972cac8827c5b7c8336ce030158fad4e913464aa4517af93e1d47`. It applies
cleanly to the verified rev0850 active tree. The replay tree matches the final
rev0851 active implementation on all **276/276** files, with no missing path,
extra path, byte-count, or SHA-256 mismatch.

The final active implementation projection is `fe9ea63a239b4b769e6c8a352c65e60b494925331294ec4986ee14607fed3b7e` over
**276 files / 17,601,745 bytes**.
