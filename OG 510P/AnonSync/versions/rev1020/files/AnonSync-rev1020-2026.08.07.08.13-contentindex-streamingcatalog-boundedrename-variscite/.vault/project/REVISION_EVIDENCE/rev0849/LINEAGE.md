# AnonSync rev0849 lineage

Rev0849 is derived only from the sealed canonical parent:

- parent revision: `rev0848`;
- parent archive: `AnonSync-rev0848-2026.07.19.14.35-atomicbusyowner-clientdataclaim-forkproof-verifierseal.zip`;
- parent archive SHA-256: `5440f1b83b6de9734338a06e7ff5d25f7355c154d58dcf97a792ff651c089985`;
- canonical archive root: `AnonSync/`;
- parent ZIP verification under the strengthened rev0849 verifier: **26/26**;
- extracted parent directory verification: **22/22**.

The newly mandatory shared callback-claim files are revision-scoped to rev0849
and later, so the stronger current verifier does not retroactively invalidate
the sealed parent.

`SOURCE_DIFF_rev0848_to_rev0849.patch` has SHA-256 `478635521cbaf711605088ef3f9095d91d7033097c7c22ebd5eb944e68182ae4`. It applies cleanly to the verified
rev0848 active projection. The replay tree matches the final rev0849 active
implementation on all **269/269** files, with no missing path, extra path, byte-count, or SHA-256 mismatch.

The final active implementation projection is `73eb67a6f93792d691ee2cdb674a44e76627f85027fa0451978d815fe68d12ac` over
**269 files / 17,535,700 bytes**.
