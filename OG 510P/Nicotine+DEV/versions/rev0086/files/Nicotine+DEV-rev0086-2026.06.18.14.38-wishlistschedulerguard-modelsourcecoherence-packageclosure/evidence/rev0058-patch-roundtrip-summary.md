# rev0058 patch roundtrip summary

The recorded rev0058 matrix was assembled from three lane-specific helper runs:

```text
github-tag-3.3.10: pass
github-branch-3.3.x: pass
github-branch-master: pass
```

Combined result:

```text
patch apply roundtrip rows: 12/12 pass
patched source-file hash rows: 15/15 pass
fixed-regression rows after patch-file apply: 21/21 pass
```

Raw fixed-regression output is in `evidence/rev0058-patch-roundtrip-rerun/`.
Lane helper JSON outputs are in `evidence/rev0058-patch-roundtrip-lane-helper-outputs/`.

The proof uses the uploaded archived source bundle, not an embedded source tree.
