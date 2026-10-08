# Session review — rev0870

## Completed

- Restored four exact OCF source payloads totaling 53 bytes: the SDT demo output and three DSC summary JSON files.
- Raised exact canonical-path coverage from 103 to **107 files** and source coverage from 16 to **20 files**.
- Added a narrow verify-first, no-clobber recovery engine for those bytes.
- Refactored canonical coverage reads into descriptor-bound, no-follow, mutation-detecting snapshots.
- Added deterministic regressions for same-size path replacement, in-place mutation, root symlink aliases, overwrite refusal, and symlinked-parent escape.
- Hardened component walking after observing this filesystem follow a directory symlink despite `O_NOFOLLOW`.
- Corrected a no-clobber cleanup defect that could unlink an existing file after an overwrite refusal.
- Removed recursive full-history ZIP-suite execution from the normal gate, retaining the inherited byte and exploit checks live and the complete suite as a release check.
- Proved that no remaining unavailable indexed path shares an exact identity already present elsewhere in the cube or recovery store.

## Remaining highest risks

Publication rights remain undecided. All 17 selected StreamFold payloads are still absent. Canonical root `README.md` remains the sole unresolved present-path mismatch. The cube still lacks 4,463 indexed files / 101,448,493 bytes.

## Next substantive frontier

There are 497 unresolved files no larger than 256 bytes. Future work should attack only families constrained by surviving generators, traces, or protocol structure, with `INDEX/files.csv` as the final hash oracle. Broad filename guessing and new registries should remain out of scope.
