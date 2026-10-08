# rev0073 U-123 native-patch verification note

`tools/probe_rev0073_u123_native_patch.py` validates the generated upstream-style test patch in a namespace separate from the canonical disposition matrix.

```text
test-only patch on unpatched source: 2 failed, 7 passed (expected)
combined prototype plus tests, target file: 9 passed
combined prototype plus tests, full units: 60 passed, 1 skipped
patch application: pass
changed-file compilation: pass
exact captured 3.3.x ref: pass
```

Outputs use `data/rev0073_u123_native_patch_*` and cannot overwrite `data/rev0073_u123_test_matrix.*`.
