# AnonSync rev0947 revision notes

## Mission

AnonSync exists to replace Resilio Sync in a named real workflow with a practical
C++ folder-synchronization product. Direct TCP, Tor, and I2P remain routes into
one authenticated reconciliation model. This revision changes the shipping
folder owner; it does not introduce another daemon, policy plane, or sync engine.

## Primary correction: deterministic-prefix starvation

Rev0946 identified a liveness defect in the local repair scan. Every pass began
at the root, traversed names in deterministic component-wise order, and charged
all regular-file bytes against one aggregate work frontier. When a stable prefix
consumed that frontier, each later pass could repeat the same prefix forever.
Suffix changes could remain unseen and a complete scan could remain impossible,
which also prevented authoritative deletion inference.

Rev0947 adds durable fair scan epochs:

- the descriptor-rooted observer can resume after an exact traversal cursor;
- the cursor comparator matches the real component-wise depth-first preorder,
  rather than incorrectly comparing flat path strings;
- one SQLite scan-progress row and an ordered, SHA-256-chained seen-path journal
  survive service restart;
- each successfully adjudicated path is staged for journal publication only
  after its idempotent path effect has committed;
- the complete segment journal is published in one immediate transaction,
  replacing the prototype's transaction-per-file design;
- deletion inference is permitted only after a complete epoch and a full ordered
  journal rehash;
- a cataloged path that is absent from the journal but physically present forces
  a new epoch rather than allowing a false deletion;
- exact schema-v1 and schema-v2 catalog cutpoints migrate transactionally to the
  schema-v3 continuation owner; near-matches still fail closed.

The aggregate byte limit is now a per-pass work frontier. It does not become an
unbounded whole-tree allowance: every individual observed file, every namespace
entry, every path, and every durable catalog/payload owner remains subject to its
existing hard admission limits.

## Audit correction: a completed-epoch absence race

The first fair-scan implementation exposed a second race during audit. A file
could be visited in an early segment, deleted before the final segment, and
remain represented in the epoch journal. Completion alone would then omit it
from absence inference, while the remote phase could immediately restore the
exact old catalog predecessor. That erased local deletion intent before the next
scan could adjudicate it.

Rev0947 fences that case. Whenever the local path is absent, the exact remote
file matching the retained catalog predecessor is deferred as an
unadjudicated-local-absence candidate, even when the current epoch just
completed. A genuinely distinct remote successor still follows the established
conflict/apply policy. The following epoch may publish the local tombstone once
it has authoritative absence evidence.

The related incomplete-epoch tombstone rule is also explicit: a remote tombstone
cannot generically remove a local regular file that has not yet been adjudicated
in the current epoch. These fences keep the asynchronous sweep conservative
without pretending it is a point-in-time filesystem snapshot.

## Refactor: one journal transaction per segment

The initial durable-cursor prototype committed one SQLite transaction for every
visited file. In WAL mode with the project's durable synchronization profile,
that could turn a large scan into thousands of commit and synchronization
boundaries. The selected implementation keeps path effects independently
committed and replayable, then publishes all seen paths from one completed
traversal segment with one prepared INSERT loop and one compare-and-swap update
of the progress head.

Crash ordering is deliberate:

1. A path effect may commit before the segment journal. If the process stops,
   that segment is replayed idempotently.
2. A segment journal may commit before completion proof. Restart reloads and
   re-attests the exact durable prefix.
3. Absence effects may commit before epoch reset. They are idempotent and the
   completion transaction is re-entered safely.
4. Epoch reset may commit before remote application. The next epoch starts from
   an empty prefix while normal remote reconciliation resumes.

A trace-backed regression requires three path inserts to produce one progress
head publication for the segment.

## Operator-visible state

Folder and service status now expose:

- `local_scan_epoch`;
- `completed_local_scan_epoch`;
- `restarted_local_scan_epoch`;
- `local_scan_seen_path_count`;
- `local_scan_resume_after_path`;
- `deferred_unadjudicated_local_absence_remote_files`.

These are diagnostics, not new tuning bureaucracy. The service process test now
proves that two six-byte files converge through two six-byte scan segments and
that the cursor survives process restart before an idle completed epoch.

## Exact nonclaims and remaining limits

This revision establishes semantic fairness, not target-scale scan efficiency.
Each segment starts from the retained root and re-enumerates and `lstat`s the
skipped prefix. The cursor prevents repeated payload work and repeated path
effects, but a long prefix still costs metadata I/O on every segment.

The scan is not a point-in-time snapshot. Already-seen edits or removals are
conservatively deferred to a later epoch; an unseen cataloged path that appears
behind the cursor forces a restart; a new uncataloged path behind the cursor is
found by the next epoch.

The hard namespace-entry ceiling still counts directories, symbolic links,
special files, and internal artifacts as well as regular files. A configuration
that admits 100,000 cataloged regular paths therefore does not promise that an
arbitrarily decorated namespace containing those paths fits the same traversal
entry limit.

A segment containing many zero-byte files can still stage a large immediate
journal transaction. Safe internal chunking requires a proof that cursor
publication cannot outrun retained directory/root identity re-attestation; it is
not added merely to make a benchmark look better.

Startup checks bind the progress head, first row, tail row, and absence of rows
past the head. The complete middle hash chain is re-read before deletion
inference. A middle-row corruption therefore fails closed no later than epoch
completion, but rev0947 does not pay a full journal rehash at every startup.

The payload store is still restart-cold without a durable metadata index, is
append-only without reachability/GC, and transfers a changed large file as a new
whole-file identity. Rename, empty-directory and metadata semantics, recovery
UX, many-share device ownership, cross-platform naming, and target-scale
Tor/I2P qualification remain product work.

## Validation

The frozen rev0947 source passed:

- GCC 14.2 complete configured graph and 254/254 registered tests;
- the 35/35 GCC product lane inside that registry;
- 49 focused observer checks;
- 225 focused folder-scan-owner checks;
- the real folder CLI continuation/restart process test;
- the 51/51 payload-store/folder-owner lexical structural audit after updating
  its ordering contract to require resumable traversal and batched publication;
- a clean Clang 17 AddressSanitizer/UndefinedBehaviorSanitizer product build;
- 35/35 serial sanitizer product tests with leak detection in 87.99 seconds and
  no sanitizer diagnostic.

The lexical audit is hygiene evidence only. It does not prove filesystem,
cryptographic, transaction, concurrency, or crash semantics; those claims are
carried by the runtime tests, source review, and explicit state-machine audit.
