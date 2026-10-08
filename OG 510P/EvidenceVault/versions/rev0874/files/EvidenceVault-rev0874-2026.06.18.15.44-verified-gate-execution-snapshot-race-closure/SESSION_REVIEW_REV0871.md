# Session review — rev0871

The session stayed on byte recovery and correctness rather than adding another registry layer.

## Delivered

- Recovered two exact PCB subject digest files, **144 bytes total**, from complete values already preserved in patch evidence and admitted only by full indexed size/SHA-256 equality.
- Raised exact current-path coverage to **109 files** and rehydratable coverage to **125 files / 4,973,641 bytes**.
- Added `scripts/safe_materialize.py` and migrated four recovery tools onto it, removing three separate publication implementations.
- Added adversarial regressions for no-clobber preservation, `O_EXCL` race cleanup, root/parent/final symlinks, mode normalization, and path aliases.
- Audited the reverse overlay history, old-side patch streams, embedded scalar evidence, and the 174-object PACT content-addressed family. No unverified bytes were admitted.

## Decisions

The canonical root README cannot be reconstructed from retained overlay history. The PACT object family remains promising but has no verified preimage. Both are left unresolved rather than guessed.

## Remaining blockers

Publication rights remain unapproved. All 17 selected StreamFold payloads remain absent. Canonical `README.md` remains the sole unresolved same-path mismatch. **4,461 canonical files / 101,448,349 bytes** remain unavailable.
