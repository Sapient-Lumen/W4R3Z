# tempfile_cleanup_mode_changes_reset_posture

This scenario keeps a subtle cleanup boundary explicit:

- `tempfile()` relies on OS cleanup when the last handle closes,
- `TempDir` and `NamedTempFile` rely on Rust destructors,
- and cleanup can be disabled explicitly.

All three may feel like “temporary state” in ordinary prose, but they are different reset/contamination postures for downstream tests.
