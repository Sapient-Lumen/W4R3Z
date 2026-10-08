# rev0058 handoff — patch-file roundtrip regression gate

This handoff layer validates the rev0057 patch files as files, not merely as outputs implied by helper scripts.

## Inputs

```text
source bundle: Nicotine-source(1).zip
source SHA256: feaa8df98bbd0f28ba00eb8d52dcc3b9b9860e8d59039c7d41a98a0117505e5b
patch source: handoff/rev0057/patches/*/strict-front-selected-stack-rev0057.patch
```

## Gate

For each archived lane:

```text
1. Extract clean source lane from uploaded source zip.
2. Forward dry-run the matching rev0057 patch file.
3. Apply the patch file.
4. Reverse dry-run the patch file after apply.
5. Confirm a second forward dry-run is rejected after apply.
6. Verify the five patched source-file hashes.
7. Run the seven selected fixed-regression artifacts.
```

## Result

```text
patch apply roundtrip rows: 12/12 pass
patched file hash rows: 15/15 pass
fixed regression rows: 21/21 pass
```

## Files

```text
data/rev0058_patch_roundtrip_apply_matrix.csv
data/rev0058_patch_roundtrip_file_hashes.csv
data/rev0058_patch_roundtrip_fixed_regression_matrix.csv
evidence/rev0058-patch-roundtrip-rerun/
evidence/rev0058-patch-roundtrip-lane-helper-outputs/
tools/probe_rev0058_patch_roundtrip_gate.py
```

## Boundary

This is archived-source proof. Live-current external filing still needs a fresh checkout or current tarball with commit identity and a current-source seven-gate refresh.
