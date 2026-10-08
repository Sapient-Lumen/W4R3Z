# AnonSync rev0857

## Mission increment

AnonSync depends on identity bytes as transition authority: manifests,
idempotency keys, conflict evidence, checkpoints, and transfer verification all
assume that equal validated values hash identically. Rev0857 makes that
assumption explicit and executable by removing ambient-locale formatting,
centralizing exact v1 tuple bytes, and streaming nested manifest identities.

## Severe defect corrected: locale-dependent SHA-256 text

`sync_domain.cpp` owned a helper that looped over raw digest bytes and inserted
each integer into `std::ostringstream` with `std::hex`, `std::setw`, and
`std::setfill`. Numeric output streams use their locale's `num_put` and
`numpunct` facets. A valid grouping facet can insert a thousands separator into
an integral hexadecimal representation. Under a grouped global locale the old
helper emitted underscore-bearing digest text instead of 64 lowercase
hexadecimal characters.

That path was used by directory scanning, existing-file fingerprinting, staged
range receipts, and staged whole-file verification. The effect could be a
fail-closed denial of service—AnonSync rejecting hashes it just created—or a
locale-dependent identity boundary if malformed text reached another layer.
The defect required no malformed peer input; changing ambient process locale
was sufficient.

All four paths now use `Sha256DigestBuilder`. The domain translation unit no
longer mentions `EVP_MD_CTX`, `EVP_Digest*`, `EVP_sha256`, `EVP_MAX_MD_SIZE`,
`std::ostringstream`, or `std::to_string`.

## Waste corrected: copied and materialized manifest identity

The former public digest APIs called helpers returning `SyncManifestEntry` or
`SyncFolderManifest` by value after validation. A digest of one entry copied
its chunk and lineage vectors; a folder digest copied every entry and every
nested vector. The code then constructed complete length-prefixed material
strings at the chunk, lineage, entry-list, entry, folder, and mutation layers.
Large manifests therefore paid avoidable copy and transient-allocation costs
before SHA-256 could consume the bytes.

Rev0857 replaces the by-value “canonical” helpers with validating const-reference
adapters. It introduces:

- `SecurityTupleFieldView`, a non-owning name/value view;
- `update_sha256_with_length_prefixed_security_tuple()`, which emits the exact
  existing tuple prefix and decimal length framing into an existing digest;
- `sha256_length_prefixed_security_tuple()`, the terminal convenience owner;
- `DecimalU64`, a fixed-buffer locale-independent counter formatter; and
- typed manifest identity functions for chunks, entries, versions, folders,
  and mutation keys.

Nested aggregate layers retain only fixed-size digest strings while traversing
existing vectors. No complete chunk, lineage, entry-list, entry, or folder
material string is constructed.

## Compatibility proof

The revision deliberately retains these established domains:

- `anonsync-length-prefixed-tuple-v1`;
- `anonsync-sync-chunk-v1`;
- `anonsync-sync-lineage-v1`;
- `anonsync-sync-folder-manifest-entry-digest-v1`;
- `anonsync-sync-manifest-entry-v1`;
- `anonsync-sync-manifest-entry-version-v1`;
- `anonsync-sync-folder-manifest-v1`; and
- `anonsync-sync-mutation-key-v1`.

The focused test builds the legacy bytes independently and compares exact
SHA-256 output for binary values containing NUL and colon bytes, maximum
64-bit counters, file and tombstone entries, folder ordering, publisher
binding, conflict-set binding, mutation operations, and 20,000 chunks. Unknown
entry-kind values fail closed.

The integrated hostile-locale test builds a real source manifest, checks
canonical whole-file and chunk digests, performs a fake-peer fetch session,
verifies range and staged hashes, and compares destination bytes. It installs a
global locale that groups every numeric digit, the condition that corrupts the
old hexadecimal stream formatter.

## Audit and refactor result

- Extracted two dependency-light identity owners from the 15,000-line domain
  unit.
- Reused one reviewed SHA-256 builder across scan and transfer verification.
- Removed whole-entry and whole-manifest validation copies.
- Registered two focused runtime targets and a fail-closed 31-check source
  audit.
- Extended the release verifier only from rev0857 onward, preserving validation
  of the sealed rev0856 parent.
- Found a CMake defect during the sanitizer lane: the new tests were compiled
  with ASan+UBSan but initially omitted from the sanitizer link-runtime list.
  The link failed, the CMake inventory was corrected, and the source audit now
  separately requires compile and link participation so a half-instrumented
  target cannot pass silently.

## Validation

Final-source evidence records:

- GCC 14.2 C++20 Debug all-target build and zero-action dependency closure;
- **154/154** registered tests in ranges 1-35, 36-44, 45, 46-54, 55-61, 62-68, 69-75, 76-83, 84-100, 101-116, 117-135, 136-154;
- **45/45** registered structural audits;
- manifest-identity audit **31/31**;
- GCC Debug focused runtime **694/694**;
- Clang 17 `-Werror` focused runtime **694/694**;
- GCC ASan+UBSan with leak detection and halt-on-error **694/694**;
- compile/link sanitizer command proof for both new executables;
- **400/400** repeated process executions and **9,000** check observations;
- parent archive SHA-256 `2f17baa705d630ec840dee93908e3d046ff74665af7325e55ec4e21225fc0b81`;
- parent verification **26/26 ZIP** and **22/22 directory**; and
- exact patch replay for **10/10** changed active files.

A single uninterrupted 154-test invocation is not claimed. The cloudtainer
terminated a foreground audit range, so final evidence uses twelve exact
non-overlapping completed ranges. The failed first sanitizer link is retained
as operational evidence and is not counted as a passing lane.

## Boundaries not crossed

This revision preserves identity bytes and hardens their implementation. It does
not prove semantic uniqueness of every identity domain, collision resistance
beyond SHA-256's standard assumption, whole-system convergence, bounded
manifest cardinality, or crash atomicity across all resources. Hostile data is
still interpreted in the principal process. The privacy and key-management
protocol remains unspecified.
