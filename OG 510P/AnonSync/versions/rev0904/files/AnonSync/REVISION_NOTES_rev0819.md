# AnonSync rev0819 revision notes

## Mission-level result

AnonSync's heart is **evidence-authorized convergence**: no path string,
successful syscall, callback, database row, signature, or prior observation is
by itself authority for a state transition. The invariant owner must bind the
exact object, generation, process incarnation, lifetime, policy, and durability
evidence needed for that transition, then preserve enough machine-readable
outcome state for retry and reconciliation to remain safe.

Rev0819 corrects a local but severe violation of that mission. Rev0818's atomic
publisher bound creation, write, rename, and directory durability to exact
handles, then used a pathname again during failure cleanup. It verified that the
temp name still denoted the writer-created inode and subsequently called
`unlinkat` on the name. Because another actor can replace that name between the
check and the delete, the observation did not authorize the later operation.

The corrected rule is:

> Ownership of an inode once observed through a pathname is not deletion
> authority over whatever object that pathname denotes later. On failure,
> sanitize only an exact retained capability; otherwise report residue and
> leave deletion to a separate authority-bound protocol.

## Exact lineage

The sole source parent is `AnonSync-rev0818-2026.07.17.14.16-outcomestate-componentwalk-crashfrontier-rebindproof.zip` with SHA-256
`6cdef4c7157d26e391b65c62fc81d6d2a860261c2eea1f9dc6609e334057cddf`. The exact parent ZIP passes 25/25 package checks and its
canonical extracted `AnonSync/` root passes 21/21. No build output, reconstructed
source, or alternate revision was used as source input.

## Sealed-parent defect reproduction

A byte-identical C++20 harness is compiled once against sealed rev0818 and once
against rev0819. Linux link-time wrapping intercepts `unlinkat`. When rev0818
enters cleanup, the wrapper moves the writer-created inode to another name,
installs a foreign regular file at the just-verified temp pathname, and lets the
real deletion proceed.

Rev0818's result is unambiguous:

- `unlinkat_calls = 1`;
- the replacement was installed;
- the foreign replacement was deleted;
- the old final generation remained intact; and
- `vulnerable = true`.

Rev0819 calls no pathname deletion and returns `vulnerable = false`. The
in-tree 12-check regression independently forces a temp-name rebind before a
failure and proves both sides of the new boundary: the foreign replacement
remains byte-exact and keeps its mode, while the displaced writer-created inode
is truncated and made private through its retained descriptor.

## Production correction and refactor

Rev0819 separates two facts that rev0818 had partially conflated:

1. **publication outcome** — whether this attempt replaced the final entry and
   whether the containing directory was synced; and
2. **residue state** — whether a pre-publication attempt may have left a temp
   artifact.

`SyncAtomicFilePublicationResidue` has two stable machine names:

- `none`; and
- `temporary_artifact_may_remain`.

`SyncAtomicFilePublicationError` now carries both outcome and residue. Its old
two-argument constructor remains source-compatible and defaults residue to
`none`; production failures use the three-argument form. Callers no longer need
to parse prose or infer cleanup authority from timing.

The allocation-free progress owner records possible residue immediately after
exclusive temp creation and before any later fallible operation. Once rename
publishes the namespace entry, that pre-publication residue state is consumed
and cannot reopen. This preserves monotonicity across callbacks, nested
exceptions, close failures, and process-exit cutpoints.

On POSIX, a pre-publication failure performs only best-effort operations on the
retained writer descriptor:

1. `fchmod(fd, 0600)`;
2. `ftruncate(fd, 0)`; and
3. `fsync(fd)`.

No `unlink`, `unlinkat`, `std::remove`, `std::filesystem::remove`, or
`remove_all` appears in the production atomic-publisher implementation. If a
name was rebound, descriptor sanitation still follows the writer-created inode,
not the replacement. If sanitation itself fails, the implementation makes no
stronger claim than possible residue.

On Windows, rev0819 similarly truncates and flushes only through the retained
handle while it remains open. The existing `MoveFileExW` path requires closing
the temp handle before publication, so failures after that point can report
residue but cannot be retroactively sanitized through a closed capability.
Windows behavior was not executed in this Linux cloudtainer.

The diagnostic text now explicitly says that a temporary artifact may remain
and that no pathname cleanup authority is implied. This is intentionally
conservative: retaining a private orphan is recoverable; deleting another
principal's replacement is irreversible corruption.

## Executable proof surface

The focused campaign after the final active-source change records:

| Obligation | Result |
|---|---:|
| State/API model | 24/24 |
| Race and path corpus | 28/28 |
| Exception/process-exit cutpoints | 144/144 |
| Unlink-authority regression | 12/12 |
| Structural publication audit | 32/32 |
| Repeated focused executions | 100/100 |

The four focused tests also pass under GCC 14 and Clang 17 with warning-as-error
flags. A scoped Clang 17 ASan/UBSan lane passes all four tests with leak
detection disabled; no full-project sanitizer or leak-sanitizer result is
claimed.

The all-target Debug Ninja graph compiled successfully. A final dependency
closure reports `ninja: no work to do`. CTest inventories 97 obligations. Four
disjoint exhaustive ranges—1–34, 35–68, 69–83, and 84–97—pass 97/97 on the
same immutable fully built tree. No single uninterrupted all-test invocation is
claimed; the segmented accounting is explicit in the evidence.

## Broader deletion-authority audit

The correction exposed a recurring architectural question: how many other
places treat a recognizable path as sufficient deletion authority? A lexical
inventory of `src/` found 480 candidate lines:

- 9 raw POSIX unlink candidates;
- 164 C `remove` candidates;
- 259 `std::filesystem::remove` candidates; and
- 48 `std::filesystem::remove_all` candidates.

A crude filename/location classifier labels 92 runtime and 388 selftest
candidates. These are triage figures, not 480 asserted vulnerabilities. Many
are fixture cleanup. Some source files also contain embedded selftest tails,
which makes the runtime/selftest split intentionally conservative.

Two next reviews have particularly high expected value:

- `src/persistence/sqlite_snapshot_seal.cpp` performs four raw unlinks around a
  staged database and its WAL/SHM/journal companions; and
- `src/replay_ledger.cpp` performs five raw unlinks across journal cleanup,
  temporary publication, and recovery.

Those paths combine durable state, sidecar sets, crashes, and stale process
ownership. They should be evaluated as protocols, not patched by mechanically
replacing one delete API with another.

## What should come next

A residue reaper should be a new invariant owner with explicit evidence and
machine outcomes. A defensible design would bind the exact directory identity,
versioned temp naming schema, process incarnation or expired lease, regular-file
type, private mode, link count, age, and absence from any live publication. It
should open and revalidate the artifact, quarantine it under coordinated
namespace authority, and only then delete. Prefix matching, mtime, PID text, or
a prior inode observation alone is insufficient.

The broader mission still needs an executable convergence algebra, a crash-cut
oracle spanning database/filesystem/receipt artifacts, disposable hostile-input
workers, and a complete privacy/key-lifecycle threat model. Rev0819 does not
claim those properties. It does establish a reusable local lesson for all of
them: **uncertainty must reduce authority, not expand it**.

## Source delta and limits

The reviewed active delta changes 11 files with 747
insertions and 117 deletions; bundled third-party source is
unchanged. The release projection binds 168 active files,
15823003 bytes, and SHA-256 `51e65c9aac7cb614245b93d7187ee62b19222bd418595db81ea0bab36ad92141`.

Explicitly not claimed:

- a portable atomic compare-and-unlink primitive;
- a general-purpose temp reaper;
- guaranteed sanitation when descriptor operations fail;
- arbitrary power-loss, torn-write, filesystem, or controller fault coverage;
- namespace locking after point-in-time parent checks;
- Windows runtime validation;
- full-project sanitizer or leak detection; or
- distributed convergence, payload confidentiality, anonymity, forward
  secrecy, post-compromise security, or key lifecycle.
