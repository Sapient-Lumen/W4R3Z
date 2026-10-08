# AnonSync rev0850 lineage

Rev0850 is derived only from the sealed canonical parent:

- parent revision: `rev0849`;
- parent archive: `AnonSync-rev0849-2026.07.19.17.04-sharedcallbackclaim-typedsealedopen-progressrevocation-packagegate.zip`;
- parent archive SHA-256: `7a61591a8d42eefde1c1bf5b9bb5fb73cfae8d5ac78db9716c08226db51776a9`;
- canonical archive root: `AnonSync/`;
- parent ZIP verification under the strengthened rev0850 verifier: **26/26**;
- extracted parent directory verification: **22/22**.

The newly mandatory authorizer-owner files are revision-scoped to rev0850 and
later, so the strengthened verifier continues to accept the sealed rev0849
parent.

`SOURCE_DIFF_rev0849_to_rev0850.patch` has SHA-256
`4d075946b61103d3daad42bc2e5bca111b47df6ed68c3965fd1bf4521291ee27`.
It applies cleanly to the verified rev0849 tree. The replay tree matches the
final rev0850 active implementation on all **273/273** files, with no missing
path, extra path, byte-count, or SHA-256 mismatch.

The final active implementation projection is
`00666156b20d482988552611d8c8c9369f54caa9bc146b53ee7a70fc4b747d60`
over **273 files / 17,567,989 bytes**.
