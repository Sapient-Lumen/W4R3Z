# AnonSync rev0945

## Mission

Replace Resilio Sync with one practical C++ folder-synchronization product whose
shipping peer service works directly, through Tor, and through I2P. This revision
serves that mission by reducing many-file payload work and exclusive-store
latency without adding another daemon or a premature operator configuration
surface.

## Product changes

- Reconciled two divergent unfinished rev0945 worktrees against the exact
  rev0944 baseline. Build results are accepted only when `CMAKE_HOME_DIRECTORY`
  names the final source tree.
- Rejected a draft that exposed payload-batch segmentation through CLI,
  linked-service configuration, provisioning, and setup. The current 256-put and
  256-MiB exact-work frontiers remain internal scheduling choices.
- Successful mutation-batch teardown publishes its complete verified payload
  index into the process-local warm cache after a final retained-root/lease
  proof. Cache publication cannot alter durable put success.
- A mutation batch safely owns the cache lifetime even if it outlives the store
  handle that created it.
- The prior cache vector is reclaimed after the exclusive file lock is released.
- A retained exact payload cutpoint lets unchanged and duplicate-content paths
  re-prove an existing payload without entering mutation authority.
- Only genuinely missing digests receive a mutation batch. Reports expose exact
  source/work and peak segment diagnostics.
- A likely same-size catalog no-op now releases an unrelated exclusive batch
  before opening and hashing the file; same-size edits reacquire only after
  exact proof.
- The final audit caught that bootstrap prose had claimed that transition before
  the canonical C++ branch implemented it. Publication stopped, code and tests
  were corrected together, and every exact-source release gate was rerun.
- The focused folder-owner timeout is 60 seconds: above the measured sanitizer
  runtime while still detecting a real stall.

## Honest limits

Every new mutation segment still enumerates, opens, and stats the complete
private payload namespace. The warm cache is process-local and restart-cold. New
local content is read once for stable observation and again for durable
insertion. There is no durable incremental payload index, rotating scrub,
reachability/GC owner, production changed-block promise, or target-scale
qualification. Rev0945 is not yet a Resilio replacement.

## Validation

See `REVISION_EVIDENCE/rev0945/validation/VALIDATION_SUMMARY.json` and the release
root `BOOTSTRAPROSE.md`. The published archive is valid only because complete GCC,
sanitizer, manifest/projection, ZIP CRC/path-policy, and clean-extraction
verification all passed on the frozen source and package.
