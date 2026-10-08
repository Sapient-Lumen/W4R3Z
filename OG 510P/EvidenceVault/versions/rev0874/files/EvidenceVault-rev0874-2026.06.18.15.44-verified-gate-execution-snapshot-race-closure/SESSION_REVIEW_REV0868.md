# Session review — rev0868

## Substance delivered

- Restored `sources/ocf_llm/examples/output_credential_demo_v242/credential_digest.txt` as an exact **72-byte** canonical file. Its bytes are the surviving `demo_report.json` `credentialDigest` value plus one LF, and the result exactly matches both the indexed size and SHA-256 `9027fea3c23dae8180fda581b02836c4f081a730ab2955346b9522d8c9c97ac8`.
- Raised at-path exact coverage to **101 / 4,586 files** and source-file coverage to **14 / 3,476**. Together with the 16 existing recovery objects, **117 files / 4,973,440 bytes** are rehydratable; **4,469 files / 101,448,550 bytes** remain unavailable.
- Closed a severe boundary defect: the old integrity lane began only after extraction and therefore could not distinguish ambiguous or hostile ZIP structure. The new validator checks the source container before extraction and binds every archived payload byte to the embedded overlay inventory.
- Added a deterministic archive builder that rejects symlinks and special files, fixes archive metadata and ordering, validates the temporary ZIP, pins the output mode to `0644`, and only then atomically publishes it outside the source tree.
- Refactored the rev0867 historical-recovery validator so later exact recoveries may improve coverage without weakening its fixed 16-object / 88,101-byte invariant.

## Audit/refactor result

The targeted adversarial suite covers duplicate names, traversal, case-fold aliases, symlink metadata, local/central filename disagreement, prefixed and trailing bytes, occupied-output preservation, and repeat-build byte identity. The extracted-tree gate remains necessary, but it is no longer treated as sufficient evidence about the ZIP that produced the tree.

## Still at highest risk

Rights closure remains human-blocked: no owner-approved root license or notice is present. All 17 selected StreamFold payloads remain absent, and `README.md` remains the sole unresolved present-path canonical mismatch. The exact digest reconstruction does not recover a credential, receipt, output, key, or private signing material.
