# rev0055 handoff — source bundle usage gate

Use this handoff when reviewing whether the uploaded source was used.

## Answer

Yes. rev0055 explicitly uses `Nicotine-source(1).zip` as the archived source bundle.

```text
SHA256: feaa8df98bbd0f28ba00eb8d52dcc3b9b9860e8d59039c7d41a98a0117505e5b
root: Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z
lanes: github-branch-3.3.x, github-branch-master, github-tag-3.3.10
```

## Proof chain

```text
1. data/rev0055_source_bundle_identity.csv
2. evidence/rev0055-source-anchor-helper-rerun.json
3. evidence/rev0055-current-upstream-gate-sourcezip-rerun.json
4. evidence/rev0055-strict-stack-sourcebundle-rerun-matrix.txt
5. data/rev0055_source_bundle_stack_rerun_matrix.csv
```

## Filing caveat

This source bundle is the archived rev0003 source snapshot. It is the correct input for the cube's archived-lane evidence. A clean current checkout or current source tarball is still required before filing against live upstream head.
