# release_debug_zero_implicit_strip_drift

This scenario exists because Cargo now documents a subtle but important change:
when debuginfo is disabled and `strip` is not set, Cargo can implicitly behave as though `strip = "debuginfo"` to remove pre-existing debuginfo from the standard library.

The fixture should prove that **P-0486** does not flatten these two situations into the same story:

- “release profile has less debuginfo than before”, and
- “the shipped build has become materially weaker for interactive debugging or symbolication”.

Expected contract behavior:
- `support-posture.report` weakens or requires review when the observed posture falls below policy.
- `debuggability-drift.diff` classifies the change explicitly instead of burying it in profile trivia.
- `artifact-handoff.manifest` still reports whether any sidecars that remain relevant were preserved.
