# AnonSync rev0856

## Mission increment

AnonSync's primary mission is to freeze the exact authority for a transition and
then make authorized replicated transitions converge. Earlier revisions made
local process, thread, SQLite generation, callback lifetime, namespace,
resource, publication, and recovery authority unusually explicit. Rev0856
moves the missing convergence half from aspiration into one executable C++
slice: deterministic resolution of concurrent manifest values.

## Severe defects corrected

### Directional conflict identity

The old helper built `anonsync-sync-conflict-set-v1` material with the fields
`local_version_digest` and `remote_version_digest` in caller order. The same
physical conflict observed from the opposite peer therefore minted a different
`conflict_set_id`. The identifier was not an identity of a conflict set; it was
an identity of one observer's orientation.

### Crossed primary versions

Every concurrent or equal-lineage divergent pair produced `RecordConflict`.
That action preserves the local file and applies the remote version. When both
peers independently made the same valid decision, peer A promoted B while peer
B promoted A. The result was deterministic locally but divergent globally.

### Misidentified losing publisher

The conflict-copy path was suffixed with `remote_device_id`, even though the
bytes being copied are the local losing file. The durable artifact name
therefore attributed the preserved content to the winner rather than its actual
publisher.

### Collision-prone artifact suffix

The conflict ID itself retained 128 SHA-256 bits, but the filesystem artifact
used `conflict_set_id.substr(0, 18)`. Nine of those characters are the literal
`conflict-` prefix, leaving only nine hexadecimal digest digits: 36 bits of
collision resistance in the artifact namespace.

## Delivered C++ boundary

`src/sync_conflict_resolution.hpp/.cpp` now owns the deterministic policy:

- explicit `SyncConflictValueKind` and `SyncConflictDisposition` enums;
- an owning `SyncConflictResolution` value with winner, loser, and canonical
  pair evidence;
- fail-closed validation of value kinds, distinct lowercase SHA-256 version
  digests, and bounded conflict scope;
- tombstone precedence for mixed file/delete races;
- a total order over immutable version digests for equal-kind races;
- an orientation-independent canonical pair that preserves kind/digest pairing;
- streamed, length-framed, domain-separated SHA-256 identity generation using
  `std::to_chars`; and
- no dependency on the core monolith, SQLite, filesystem, stream formatting, or
  ambient locale.

The domain planner now maps the typed result as follows:

- local winner: `PublishLocalFile` or `PublishLocalTombstone`;
- remote winner with local tombstone: apply the remote tombstone without fake
  file-copy work; and
- remote winner with local file: `RecordConflict`, preserving the local loser
  before applying the remote winner.

Only the losing peer mints conflict-copy authority. The artifact path uses the
local losing device ID and the entire 128-bit v2 conflict ID.

## Executable convergence oracle

The focused policy corpus covers orientation reversal, stable winner/loser
identity, folder/path/kind binding, file/delete semantics, tombstone/tombstone
semantics, malformed digests, identical versions, unknown enum values, control
bytes, and exact byte ceilings.

The integrated corpus uses `build_sync_manifest_diff_plan()` and
`build_sync_local_apply_plan()` rather than a duplicate implementation. It
proves:

- complementary views select exactly one publisher and one preserving loser;
- both views agree on exact winner and loser version digests;
- the losing plan's conflict ID equals the independently recomputed reversed ID;
- grouped global numeric locale cannot change identity bytes;
- the local apply plan names the actual losing publisher and retains the full
  conflict ID as the terminal suffix;
- duplicate winner delivery is a no-op;
- duplicate ordinary conflict-artifact delivery is set-idempotent; and
- all six delivery permutations converge for three files, two files plus a
  tombstone, and three tombstones.

The expected result is independent of the implementation: maximum file digest
when every value is a file, maximum tombstone digest when any tombstone exists,
and the set of every losing file digest preserved as an artifact.

## Audit and refactor work

- Extracted the policy from the 15,000-line domain translation unit into a
  separately linked, 170-line implementation leaf.
- Registered the owner source in the invariant-owned CMake inventory.
- Added focused test and sanitizer targets without pulling the policy test
  through the domain monolith.
- Added a fail-closed 31-check structural audit covering typed ownership,
  dependency direction, framing, locale independence, total ordering, identity
  binding, domain delegation, full artifact identity, generated histories,
  duplicate delivery, and release-package requirements.
- Extended the release verifier only from rev0856 onward, preserving successful
  verification of the sealed rev0855 parent.
- Refactored broad legacy fixtures to orient remote conflict values according to
  production policy instead of assuming “remote always wins.”

## Compatibility

New plans mint `anonsync-sync-conflict-set-v2`. Persisted v1 plans and
checkpoints are not recomputed; recovery consumes their stored portable
`conflict_set_id` and path evidence. This preserves completion authority for
in-flight work. A fresh plan for the same still-unresolved pair can produce a
new v2 artifact name, so a one-time duplicate preserved copy is possible when a
v1 artifact already exists. Rev0856 deliberately avoids destructive historical
renames.

## Validation

Final evidence records:

- complete GCC 14.2 C++20 Debug all-target build;
- one expected delayed relink wave followed by a true zero-action Ninja build;
- **151/151** registered CTests in exact ranges 1–34, 35–55, 56–77, 78–114,
  and 115–151;
- **44/44** registered structural audits;
- GCC Debug focused runtime: **659/659** checks;
- Clang 17 `-Werror` focused build and runtime: **659/659** checks;
- focused repeatability: **200/200** process runs and **5,500** aggregate check
  observations;
- conflict-convergence audit: **31/31**;
- rev0855 parent archive SHA-256
  `29f29f9d3f19d0e154572e4adb0da7dbeaa6e78313d6917f0a11cab7d9c24ab9`;
- parent verification: **26/26 ZIP** and **22/22 directory** checks; and
- exact source-patch replay plus a recomputed active implementation projection.

The sanitizer and final package-verifier results are recorded in the immutable
validation summary and release gate generated after this note.

## Boundaries not crossed

This revision proves a deterministic conflict-primary slice, not whole-system
strong eventual consistency. It does not model message omission, unbounded
partitions, Byzantine updates, object recreation epochs, rename graphs,
membership or key epochs, multi-resource crash cutpoints, or externally visible
effects in one operation algebra. Conflict artifacts are treated abstractly as
ordinary set-union files after creation; full network dissemination remains to
be exercised.

No claim is made for confidentiality, anonymity, metadata hiding, forward
secrecy, post-compromise recovery, hostile-worker isolation, secure erasure,
ThreadSanitizer, full-project sanitizers, Release all-target behavior, or
Windows runtime behavior.
