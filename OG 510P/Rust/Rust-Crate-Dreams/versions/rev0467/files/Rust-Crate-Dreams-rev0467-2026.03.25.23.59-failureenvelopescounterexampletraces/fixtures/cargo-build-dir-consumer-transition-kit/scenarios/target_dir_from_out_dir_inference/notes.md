# Target-dir from OUT_DIR inference

This scenario separates two things people often blur together:

- build-script-owned outputs that really do belong under `OUT_DIR`, and
- guessed recovery of target-dir or workspace layout from `OUT_DIR` or a helper binary path.

The crate should not pretend those are the same contract.
