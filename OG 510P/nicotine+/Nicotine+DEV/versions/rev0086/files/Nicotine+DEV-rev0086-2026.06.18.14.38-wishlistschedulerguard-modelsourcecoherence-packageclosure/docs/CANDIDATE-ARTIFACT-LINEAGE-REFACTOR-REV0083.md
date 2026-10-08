# Candidate artifact lineage refactor — rev0083

## Defect in the cube

The rev0081/rev0082 candidate lived at an unversioned-looking path:

```text
maintainer_artifacts/search-rekey-01/search_again_fresh_token_rekey.patch
```

Multiple historical result records bind that exact path and SHA-256. Editing it
in place would silently make old unit and consumer evidence refer to different
bytes, while a package could still look internally plausible.

## Correction

The old file remains byte-for-byte immutable at SHA-256:

```text
f4120f3cf10e70d289e826acc7fd17359088595a156c5bd2c1947fd896c77101
```

The corrected prototype uses a revision-qualified path:

```text
maintainer_artifacts/search-rekey-01/search_again_mode_owned_rekey_rev0083.patch
00a940afc12eb4d634323a27e8d8ade849aed2a800786caf6b16728a1060371b
```

Machine authority now lives in:

```text
data/current_candidate_artifact_contract.json
tools/audit_current_candidate_artifacts.py
```

The audit verifies artifact bytes, current/superseded lifecycle, revision-qualified
current naming, three historical evidence bindings, and that no current Search
Again epoch packet selects a patch. Five negative-control mutations must be
rejected.

This is a general cube rule: evidence-bound candidate files are immutable. A
changed hypothesis receives a new path and a new lineage entry rather than an
in-place overwrite.
