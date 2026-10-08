# AnonSync rev0818 revision notes

## Mission-level result

Rev0818 turns atomic JSON publication from an implicit syscall sequence into an
**evidence-classified transition protocol**. The corrected rule is:

> A caller may decide retry and recovery policy only from the strongest effect
> the publication owner actually established: no rename, rename with directory
> durability still unknown, or rename followed by a successful directory sync.
> Path spelling, diagnostic text, and “the last syscall probably failed before
> anything happened” are not transition evidence.

This is the local filesystem form of AnonSync's central mission: state changes
must carry owner-verified evidence precise enough to survive concurrency,
exceptions, process death, replay, and partial failure.

## Exact lineage

The sole source parent is `AnonSync-rev0817-2026.07.17.12.34-atomicpublish-dirfdowner-uniquetemp-raceproof.zip` with SHA-256
`761e7364553c39bd121c3b0407a3b3a92370153ec490390045d074d65ec2a3c1`. The exact parent ZIP passes 25/25 package checks and its
canonical extracted `AnonSync/` root passes 21/21. No build output,
reconstructed source, or alternate revision was used as source input.

## Sealed-parent defect reproduction

A byte-identical C++20 harness requests publication to
`root/link/subdirectory/report.json`, where `link` is an intermediate directory
symlink to `root/real`. Against sealed rev0817, the call reports success and the
payload appears in the symlink target. Against rev0818, the call reports failure,
creates no redirected file, and identifies the link-bearing component.

The defect existed because rev0817 rejected a symlink only when it was the
terminal parent. Earlier path components were still resolved by the kernel's
ordinary pathname walk.

## Production correction and refactor

Rev0818 adds a small, one-way ownership stack:

```text
sync_atomic_file_publication_state
        -> sync_atomic_file_publication
        -> anonsync_core_lib
```

The allocation-free state owner records cleanup authority, namespace
publication, and parent-directory synchronization. Public failures carry one of
three machine-readable outcomes:

- `not_published`;
- `published_durability_indeterminate`;
- `published_and_directory_synced`.

The exception remains derived from `std::runtime_error` for compatibility. It is
deliberately non-final because the C++ standard's `throw_with_nested` mechanism
cannot synthesize a nested wrapper around a final class. A retained first run
passed only 87/96 cutpoint checks and exposed that mistake; the final corpus
passes 133/133. Already-typed nested failures are now recomposed from the current
transition state instead of escaping with stale outcome authority.

On POSIX, publication now:

1. converts the requested destination to an absolute lexical path;
2. opens `/` and walks every parent component with
   `fstatat(AT_SYMLINK_NOFOLLOW)` plus `openat(O_NOFOLLOW|O_DIRECTORY)`;
3. binds each path observation to the opened descriptor's exact device/inode;
4. creates a private, exclusive temp inode relative to the pinned terminal
   directory;
5. writes and syncs all payload bytes;
6. re-proves the temp path's exact inode, one-link exclusivity, and absence of
   group/other permission bits;
7. reopens the full parent chain and proves the terminal identity before rename;
8. atomically replaces the final entry with same-directory `renameat`;
9. records publication before any callback or diagnostic can fail;
10. syncs the pinned parent directory and records that evidence; and
11. re-proves that the configured parent path still names the pinned directory
    after durability was established.

A deterministic post-sync rebind no longer returns false success. The call
throws `published_and_directory_synced`, preserving the exact fact that the new
generation is durable in the pinned directory even though the configured path
was observed detached.

These rechecks are point-in-time observations, not namespace locks. Without
external coordination, another principal can always rebind after the final
check. The API and evidence do not claim otherwise.

## Executable crash frontier

The internal observer enumerates eleven reviewed POSIX frontiers from temp
reservation through descriptor closure. The focused oracle interrupts every
frontier in two ways:

- a thrown exception verifies typed outcome, nested cause, visible generation,
  cleanup authority, and residue; and
- a forked child calls `_exit`, after which the parent classifies the exact
  namespace shape: old final plus one private temp before rename, or one complete
  new final and no temp name after rename.

The corpus also forces pre-rename parent rebinding, post-sync parent rebinding,
an already-typed stale exception, and a widened temp mode. All fail with the
expected state and without guessed deletion.

## Validation

- Pure state owner: **20/20** checks.
- Race and path runtime: **28/28** checks.
- Exception/process-exit cutpoint oracle: **133/133** checks.
- Structural publication audit: **30/30** checks.
- Focused stress: 25 consecutive iterations of each of three runtime tests,
  **75/75 executions**.
- GCC 14.2 and Clang 17 focused builds pass with `-Werror`.
- Clang 17 ASan/UBSan focused CTest passes 4/4 with leak detection disabled.
- The complete Debug graph builds every target; command-window limits required
  resuming the same immutable Ninja tree. The final dependency closure reports
  `ninja: no work to do.`
- The complete project CTest gate passes **96/96** in 30.78 seconds.

Eleven active files changed: 1662 inserted and
159 removed lines. No bundled third-party file changed.
The active projection contains 167 files and
15795038 bytes with SHA-256 `76eacfe32e3b54e05eabd894d70e0490b78467bbe09ec1ffe4f5c5fd7dd16017`.

## What remains

The process-exit model is not a power-loss model. The next publication oracle
should interpose write, fsync, rename, directory sync, and close failures in a
disposable worker, force storage cutpoints, and evaluate filesystem state plus
higher-level receipts/checkpoints as one recovery protocol.

Typed outcomes are now available, but production call sites still mostly let the
exception propagate. Their retry/reconciliation policies should consume these
outcomes explicitly rather than treating every report or heartbeat failure as
identical.

A residue reaper remains a separate authority boundary. It needs a versioned
namespace, exact file type and inode evidence, age, and preferably process-
incarnation or lease evidence. A recognizable temp prefix is never deletion
authority.

The larger mission gaps remain: an executable distributed convergence algebra,
a disposable hostile-database worker, and a complete confidentiality,
metadata-leakage, enrollment, key-rotation, revocation, recovery, forward-
secrecy, and post-compromise-recovery design. `sync_domain.cpp` is still
15,257 lines and remains a major build and review
cost.
