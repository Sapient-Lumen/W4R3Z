# AnonSync rev0852 lineage

Rev0852 is derived only from the sealed canonical parent:

- parent revision: `rev0851`;
- parent archive: `AnonSync-rev0851-2026.07.19.19.38-ownedpolicycontext-retireaftermutex-centralfork-auditseal.zip`;
- parent archive SHA-256: `0bf0b2d94244e002a0e24f7443fc8eded0a603beb2c5def9ed99244e85aea5b6`;
- canonical archive root: `AnonSync/`;
- parent ZIP verification under the rev0852 verifier: **26/26**;
- extracted parent directory verification: **22/22**.

The rev0852 verifier adds the two integrated typed-policy consumers and the
upgraded composed authorizer audit to the revision-scoped mandatory inventory.
Those requirements begin at rev0852, so the same verifier continues to accept
the sealed rev0851 parent.

`SOURCE_DIFF_rev0851_to_rev0852.patch` has SHA-256 `19443aa2794d4b038900bfb6ecbbb346e807c21d6f9c874c8a29a370fa917daf`. It applies
cleanly to the verified rev0851 active tree. The replay tree matches the final
rev0852 active implementation on all **276/276** paths, with no missing file,
extra file, byte-count mismatch, or SHA-256 mismatch.

The final active implementation projection is `adb304a75f7ff6f4718be63b5e9931fc4ed59002d96158405355aff6e84c4b64` over **276
files / 17,622,237 bytes**.
