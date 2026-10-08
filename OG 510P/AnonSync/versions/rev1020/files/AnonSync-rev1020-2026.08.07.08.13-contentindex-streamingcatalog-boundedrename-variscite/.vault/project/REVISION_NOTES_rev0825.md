# AnonSync rev0825 revision notes

## Mission-level result

AnonSync remains an **evidence-authorized convergence engine**. Rev0825 makes a
reset receipt describe one durable event rather than one observation attempt,
and gives immutable evidence a namespace transition that cannot overwrite a
competing entry.

## Severe parent gaps

Rev0824 receipt v3 was constructed from `SqliteReplayLedgerResetResult` after
the reset call. It serialized `outcome`, `connection_owner_generation`, and
`state_advanced_after_commit`. Exact first execution and exact recovery could
therefore describe the same committed reset with different bytes. A later write
could change the receipt even though replay correctly performed no second
reset. That weakens content addressing, external witnessing, deduplication, and
operator comparison precisely where deterministic recovery evidence is needed.

The CLI then published that receipt through the generic replace-capable report
publisher. Its earlier alias fence protected the ledger family and request, but
an unrelated regular file appearing at the receipt name after checks could be
atomically replaced. Preflight alone cannot close that check/use race.

## Production correction

Receipt format v4 is emitted by
`sqlite_replay_ledger_reset_documents.cpp`, a separately linked production
owner. Its durable receipt function accepts only the fully validated request and
the lowercase SHA-256 of the exact request-file bytes. It validates the request
before emitting bytes and deterministically projects:

- protocol format and backend;
- exact request digest, intent, operator, and reason digest;
- normalized ledger path;
- complete prior namespace identity and logical-state expectation;
- deterministic empty post-reset state and receipt-derived ledger identity;
- the in-place SQLite commit protocol; and
- the fresh immutable receipt recovery protocol.

Attempt-local outcome, owner generation, and later-state observations are
excluded. Inspection reporting remains a separate function and may retain
observation metadata without contaminating the durable receipt.

The reset CLI now renders the canonical receipt and performs create-new
preflight before calling the reset owner. After a committed or recovered durable
outcome, it publishes the precomputed bytes through an immutable create-new
wrapper. A failed postcommit publication returns the existing recoverable status
and instructs the operator to rerun the exact request to a fresh absent path.

## Atomic publication refactor

The focused publication owner gained an explicit
`AtomicFilePublicationDisposition` with replacing and create-new modes. The
create-new path reuses the existing directory-descriptor, private temp file,
full-write, file-sync, temp-identity, parent-identity, typed-outcome, and
directory-sync protocol. Its final Linux transition is the typed libc
`renameat2` entry point with `RENAME_NOREPLACE`; the earlier raw variadic
`syscall` experiment was removed.

An occupied regular destination, symlink, non-regular entry, or racing creator
is not replaced. The deterministic observer corpus creates a competing final
entry after final-name revalidation and proves its bytes and inode survive. The
publisher reports `NotPublished` plus possible writer-owned temp residue rather
than racing a guessed pathname deletion.

On platforms without an atomic no-replace rename primitive, create-new fails
closed. The Windows implementation selects non-replacing move semantics but was
not executed in this Linux cloudtainer.

## Audit/refactor result

Receipt and state-report formatting no longer live in the large CLI translation
unit. The focused documents library has no core dependency and is protected by
configure-time ownership guards, sanitizer inventory, a dedicated 18-check
byte-contract executable, and a 36-check cross-file source audit.

The existing reset audit was upgraded from receipt-v3 assumptions to v4
canonical-event and fresh-path recovery invariants. The publication audit now
requires the typed no-replace primitive, forbids raw variadic syscall usage, and
requires a deterministic competing-creator oracle.

## Validation

- exact parent archive SHA-256:
  `a1e98d7cf5b721488195f1cf094640af4768565ceeefc5a0987cd9923df3c6c4`;
- exact rev0824 parent: ZIP 25/25 and directory 21/21;
- source patch replay: 188/188 current active files and 16/16 changed files;
- source delta: 1,501 insertions and 258 deletions;
- GCC 14 Debug all-target build: passed; final dependency closure: no work;
- complete 109-test inventory covered by three disjoint final-source CTest
  ranges: 21/21, 27/27, and 61/61;
- canonical reset documents: 18/18 checks;
- atomic publication runtime corpus: 38/38 checks;
- publication caught/crash/race cutpoints: 149/149 checks;
- reset owner: 67/67 checks;
- CLI integration oracle: 380/380 checks;
- source audits: 197/197 checks;
- Clang 17 warning-as-error focused graph: 3/3; and
- GCC 14 ASan/UBSan focused graph: 3/3 with leak detection enabled.

Longer aggregate CTest invocations reached 108/109 before the cloud command
ceiling terminated the command. The complete-inventory claim is therefore the
explicit union of three non-overlapping passing ranges; a single uninterrupted
109-test gate is not claimed.

## Highest-priority next work

Build a deterministic VFS/application cutpoint model over the complete protocol:
`BEGIN IMMEDIATE`, each mutation, WAL write and sync, commit classification,
postcommit verification, receipt temp reservation, payload write, file sync,
atomic no-replace rename, directory sync, process exit, and compound I/O
failures. The oracle must classify every cut as denied, committed/recoverable,
or durably published from filesystem evidence rather than process-local return
values.

After that, move hostile SQLite interpretation into a disposable worker with
CPU, memory, wall-clock, descriptor, syscall, and filesystem ceilings, and then
resume the independent convergence algebra for replicated operations.

No arbitrary power-loss, hostile same-UID namespace isolation, full-project or
bundled-SQLite sanitizer, Windows runtime, distributed convergence,
confidentiality, anonymity, metadata-hiding, key-lifecycle, or secure-erasure
property is claimed.
