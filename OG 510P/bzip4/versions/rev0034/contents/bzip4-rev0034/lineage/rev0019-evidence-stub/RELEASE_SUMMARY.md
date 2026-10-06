# bzip4 rev0019 release summary

rev0019 is a cumulative recovery-and-hardening release. It preserves the last packaged cumulative rev0011 source and rebuilds the most important unarchived scheduler and cube-lifetime contracts without pretending transient worktrees were released intact.

## Main changes

- Correct minimum-grain lane activation using floor division.
- Explicit active-only and real all-retained wake/ack dispatch modes.
- Deterministic initial lane assignments and ordinal-bound result identity.
- Saturating no-throw runtime telemetry.
- Descriptor-owned anonymous spools with cursor lifetime safety and generation invalidation.
- Canonical exact-reference snapshot construction with no chains, gaps, or hidden retained bytes.
- Bounded ZIP central-directory preflight with central/local reconciliation, unsafe-path reporting, record-overlap checks, and unsigned-descriptor CRC/signature ambiguity handling.
- Updated strategy ledger: 60% compatible speed/memory/decode, 25% production cube path, 15% bounded ratio research.

## Claims

This release promotes correctness infrastructure and a scheduler policy contract. It makes no universal compression-ratio or throughput claim. The included dispatch measurements are microbenchmarks, not BZ3 throughput measurements.

## Validation

- Release build and CTest: **not passed**
- GCC ASan/UBSan: **not passed**
- ThreadSanitizer: **not passed**
- Clean-staging audit/build/CTest: **not passed**
- Canonical payloads embedded: **no**

See `research/results/rev0019/final-validation-status.json` for exact gate statuses and `docs/` for the strategy and audit record.
