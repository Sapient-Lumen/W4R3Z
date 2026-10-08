# Revision notes — rev0984

## C++ product move

- Added a required `--receipt ABSOLUTE_RECEIPT` selection to
  `database-recovery-replace`.
- Added a bounded checksum-framed immutable replacement receipt binding the
  deployment, exact selected pathnames by digest, original current expectation,
  complete candidate artifact, and complete displaced rollback artifact.
- Added an exact restart classifier for displaced-current,
  candidate-installed/epoch-pending, and recovery-successor states.
- Added idempotent completion: a fully completed action reopens and re-proves
  its database and artifacts without another mutation.
- Added receipt-only recovery that may recreate the rollback only from the exact
  still-current displaced database.
- Added fail-closed rejection of unknown and ambiguous continuity.
- Advanced the local response to
  `anonsync.local-database-recovery-replacement.response.v3` with per-invocation
  effect accounting, final candidate/rollback pathname reproof, the database
  cutpoint bracket, and explicit receipt and hostile-local-writer nonauthority.

## Audit/refactor

- Centralized the exact optional-file absence classifier shared by rollback and
  receipt paths. Only exact absence is converted to `nullopt`; every other open
  or observation failure remains terminal.
- Released the resident displaced image before reopening the durable rollback,
  avoiding an unnecessary three-complete-image peak. Final success also
  releases resident candidate/rollback images and independently recaptures
  those pathnames one at a time inside an exact final-database cutpoint bracket.
- Added an early representable-successor fence: a candidate at maximum recovery
  epoch or state generation is rejected before a new receipt, rollback, or
  database effect can make an impossible action durable.
- Removed the superseded idea of a mutable five-stage progress journal. The
  immutable receipt never becomes effect authority; the active database is the
  restart classifier.
- Extended the real process oracle with independent digest recomputation and
  exact crash-cutpoint reconstruction.

## Explicit boundaries

The command remains offline and primary-replica-database-only. It does not
restore a complete share, does not preserve raw SQLite family inode identity,
and does not provide trusted time or external anti-rollback authority. Final
pathname reproof is not a continuous name reservation and does not exclude a
noncooperating same-UID or privileged artifact writer.

## Validation

Exact rev0984 active source passed a fresh GCC 14.2 Debug graph (536/536 configured build edges), all 262/262 registered tests in an indexed final-source replay (261/261 immutable-preseal tests plus the final documentation-sensitive structural audit), and an independent 41/41 product replay. Focused GCC proofs passed 334 SQLite-owner checks, 38 deployment-binding checks, 102 snapshot-seal checks, 53 SQLite live-backup/replacement checks, 470 folder-owner checks, and the shipping database backup, recovery, replacement, and restart oracle passed 598 checks. Source audits passed 24/24 bounded-reader checks, 41/41 database-replacement checks, and 404/404 structural authority checks. A fresh Clang 17 Debug product dependency graph completed 247/247 edges with AddressSanitizer and UndefinedBehaviorSanitizer; all 41/41 product tests passed with leak detection and halt-on-error, including the direct 470-check folder-owner proof at 1,481,008 KiB peak RSS, and focused sanitized proofs passed the same 334, 38, 102, and 53 checks. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0983 parent SHA-256 matched 64ef96593d809861275fe7b9ec5fbf67554a25c23b6e543de70cfe9fd59519b6 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 12/12 changed active files and the complete 583-file projection byte-for-byte and by mode. The final active implementation projection contains 583 files / 27,098,385 bytes with SHA-256 48c4b04bb58f482b3dc8dc853ba951d78941ccbea552ddbb3e442a0b2ede2419. Validation excluded overlapping Ninja invocations, vanished build trees, divergent source authorities, interrupted nonterminal runs, and every result not bound to the frozen exact C++ source or the final prose-and-audit seal. The final wrapper directory and ZIP remain publication-gated on the exact manifest, package verification, CRC integrity, canonical paths, absence of symlinks, and clean-extraction path/byte/type/mode equality.

## Archive

`AnonSync-rev0984-2026.08.03.12.22-receiptresume-pathreproof-successorfence-grandidierite.zip`
