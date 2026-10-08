# AnonSync rev0842

## Mission increment

A durable row, hash-chain transition, signed snapshot, journal, or bounded document must
come from one exact opened observation and one owning validated value. Hashing,
serialization, trust evaluation, recovery, and publication may not independently traverse
broad live state.

## Delivered

- Shared dependency-light C++ frozen-publication primitives for bounded machine text,
  locale-free integers, UTF-8/control/hash/base64url/canonical-UTC validation, fixed JSON
  escaping, and named length framing.
- `FrozenLocalJsonlReplayEntry` owning every field in one local replay row. Entry hash and
  JSON now derive from the same value.
- Exact-field decode, hash verification, and byte-for-byte canonical re-encoding for local
  ledger load and journal recovery.
- `FrozenLocalJsonlReplayJournal` owning the complete recovery witness.
- Explicit local ceilings: 64 MiB ledger, 200,000 rows, 64 KiB row/hash/journal, exact JSON
  integer domain, and bounded individual fields.
- Batch staging now appends frozen rows directly instead of copying the complete line
  vector for each row, removing an actual O(N^2) batch-copy path.
- `FrozenEffectTransitionRecord` used by both SQLite transition append and reload
  verification, with bounded locale-free material and exact counter limits.
- Sequence increment overflow frontiers rejected before mutation.
- `FrozenSqliteSnapshotManifestV2Payload` owning all sixteen signature-covered fields.
  Signing digest, signature verification, trust checks, and snapshot comparisons consume
  the same frozen value.
- Legacy snapshot and durable-hash bytes remain compatible, but delimiter-bearing controls
  are rejected so the accepted newline-delimited subsets are injective.
- Shared bounded regular-file reads now reject final-component symlinks, special files,
  excess bytes, and observable mutation during the read. Mutable ledger/journal reads also
  require one filesystem link.
- Removed the duplicate runner-local bounded reader.
- Manual fixed JSON escaping, an explicit generic read-failure check, and an OpenSSL HMAC
  key-length guard.
- Focused C++ corpora: bounded reader 15, local JSONL 31, effect intent 34, transition
  record 20, snapshot publication 31, snapshot verifier 27, signed transition 8, batch 12,
  and journal hardening 14 checks.

## Parent defects reproduced by source evidence

The sealed rev0841 parent copied `canonical_lines` on every batch-stage append, producing
quadratic line copying. Its snapshot signing input traversed the broad parsed JSON object
separately from later trust and snapshot comparisons. Its runner-local `ifstream` reader
capped bytes without the stronger opened-object guarantees now shared by production.

See `REVISION_EVIDENCE/rev0842/defect/`.

## Validation

- GCC 14.2 Debug all-target build: **PASS**.
- Final dependency closure: `ninja: no work to do.`
- Complete registered inventory: **136/136** in eight exact non-overlapping ranges.
- Registered source/architecture audits: **39/39**.
- Post-final-relink focused CTest: **8/8**.
- Clang 17 `-Werror`, full `anonsync_core` build plus focused runtime: **9/9**.
- GCC 14 ASan+UBSan with leak detection, extracted changed leaves: **5/5**.
- Source patch replay: **246/246** active files exact on the sealed rev0841 parent.

## Architectural interpretation

Rev0842 extends the project's strongest local doctrine and removes a real scaling defect.
It also exposes the next proof boundary more sharply: file fsync is not directory-entry
durability, and final-component `O_NOFOLLOW` is not all-component namespace confinement.
The next local priority is one cross-resource crash oracle plus a directory-descriptor
namespace owner. The next product-defining priority remains an executable distributed
convergence algebra and a real privacy/device-key protocol.

## Scope limits

No general RFC 8785/JCS compliance, replacement of every legacy newline format, arbitrary
power-loss completeness, `openat2` path confinement, full-project sanitizer, Release
all-target build, one uninterrupted 136-test gate, Windows runtime, distributed
convergence proof, payload confidentiality, anonymity, metadata hiding, forward secrecy,
post-compromise recovery, hostile-worker sandbox, or secure erasure is claimed.

## Handoff

See `REVISION_EVIDENCE/rev0842/AUDIT.md`, `RESEARCH.md`, `NEXT_WORK.md`, and
`validation/VALIDATION_SUMMARY.json`.
