# AnonSync rev0817 revision notes

## Mission-level result

Rev0817 repairs a local publication boundary where a pathname convention was
mistaken for exclusive ownership. Heartbeat and CLI JSON reports were nominally
written through a temp-file-and-rename sequence, but the temporary name was
deterministic for a process and payload. Concurrent writers of identical bytes
therefore shared one pathname, and every caller was allowed to delete that path
as presumed stale.

The corrected rule is:

> A publisher may clean up only the exact temporary inode it exclusively
> created, only before namespace linearization. A path pattern, PID, payload
> digest, or successful earlier lookup is not cleanup authority.

This is the same mission-level pattern that guides the rest of AnonSync:
observations become authority only when the invariant owner proves exact object
identity, scope, lifetime, and transition state.

## Exact lineage

The sole source parent is `AnonSync-rev0816-2026.07.17.10.03-tristate-allocwalk-retryauthority-errorbuffercull.zip` with SHA-256
`a0c395cdc67def3e86d10ba9a75aaeae6ff68863bb2bec40ac16d988653bef37`. The exact parent ZIP passes 25/25 package checks and its canonical
extracted `AnonSync/` root passes 21/21. No build output or reconstructed source
was used as input.

## Reproduced parent defect

A byte-identical 12-thread harness executed 12 publications per thread, all to
one destination and all with the same 8 MiB payload. Against the sealed rev0816
writer, 129 of 144 calls failed. The failures were not theoretical: writers saw
exclusive-create `EEXIST` after another writer reserved the shared deterministic
name, or rename `ENOENT` after another writer removed or consumed that name.

The same harness linked to rev0817 completes 144/144 publications, reports zero
exceptions, verifies the final file is one complete payload, and finds no
module-owned temp residue.

## Production correction and refactor

The embedded writer moved out of `sync_domain.cpp` into the focused
`anonsync_sync_atomic_file_publication` library. Both the heartbeat path and
operator CLI include its 24-line API and use one 592-line implementation. CMake
fails configuration if that source drifts back into the core source list or if
the focused library/test acquires a reverse core dependency.

On POSIX systems each call now:

1. resolves and validates the final basename;
2. rejects a terminal parent symlink and binds the path's `lstat` identity to an
   opened directory descriptor's `fstat` identity;
3. reserves a unique private temp entry with `openat(O_CREAT|O_EXCL)`, PID, and
   a monotone per-call nonce—not payload bytes;
4. writes the complete payload, handling short writes and `EINTR`;
5. syncs the temp inode and re-proves that the temp pathname still names that
   exact device/inode pair;
6. rejects an existing final symlink or non-regular object without following it;
7. performs same-directory `renameat` under the pinned descriptor; and
8. syncs the directory entry.

Cleanup occurs only before rename and only after exact inode revalidation. Once
rename succeeds, the final path is already published. A later directory-sync or
descriptor-close error says so explicitly and reports durability as
indeterminate rather than attempting destructive rollback.

The Windows fallback now uses a unique `CREATE_NEW` file, `FlushFileBuffers`, and
`MoveFileExW(REPLACE_EXISTING|WRITE_THROUGH)`. Because pathname identity cannot
be re-proved after the temp handle must close for `MoveFileExW`, a failure leaves
possible residue rather than risking deletion of a replacement. Windows runtime
behavior was not executed in this Linux cloudtainer and is not claimed.

## Environment-specific finding

This Linux 4.4/overlayfs cloudtainer allowed
`open(O_RDONLY|O_DIRECTORY|O_NOFOLLOW)` to succeed on a terminal directory
symlink in a focused probe. Rev0817 therefore does not treat flags as proof. It
requires an explicit non-symlink `lstat` observation and exact `st_dev/st_ino`
match to the opened descriptor. That check also rejects a path whose identity
changes during open.

## Runtime and audit proof

The focused executable passes 23/23 checks. It covers create and replacement,
effective 0600 mode, final symlink and directory rejection, terminal parent
symlink rejection, preservation of the exact legacy predictable temp filename,
100 same-payload threaded publications, 48 distinct-payload publications with
whole-file linearization, eight forked writers, CLI delegation, and residue
inventory. Twenty-five consecutive focused iterations pass.

The structural audit passes 20/20 and binds API ownership, monolith extraction,
dependency direction, both callers, unique temp reservation, directory identity,
final-path policy, full-write and sync, inode revalidation, rename and directory
sync, cleanup authority, adversarial tests, sanitizer registration, CTest
registration, and package-verifier inclusion.

## Validation

- The complete GCC 14.2 Debug graph built every target. Command-window limits
  required resuming the same immutable Ninja tree; no single uninterrupted
  fresh-build timing claim is made. The final invocation reports
  `ninja: no work to do.`
- The complete project CTest gate passes 94/94 in 27.29 seconds.
- The CMake GCC ASan/UBSan focused lane passes 23/23 with leak scanning disabled.
- A standalone Clang 17 ASan/UBSan `-Werror` lane passes 23/23 with leak scanning
  disabled.
- GCC ThreadSanitizer passes the full 23-check threaded/forked campaign without a
  race report.
- LeakSanitizer startup with detection enabled crashes in the sanitizer runtime
  at `0xffffffffff700450` on this old kernel; leak detection is explicitly not
  claimed. A full-project sanitizer claim is also excluded.

Eight active files changed: 1399 inserted and 119 removed lines.
No bundled third-party file changed. The active projection contains
162 files and 15729241 bytes with SHA-256
`7ebb652ec446505677e7660e6fb82f0af3752ea24e23cbaedad6c012bd85b1e7`.

## What remains

The next local reliability owner should be an injectable publication cutpoint
model. It should enumerate write, file-sync, rename, directory-sync, close, and
process-crash frontiers and classify the recoverable state rather than assuming
that a happy-path test proves durability. The oracle should preserve the crucial
distinction between failure before rename, visible publication with unproved
directory durability, and durable completion.

Residue cleanup must remain separate from publication. A future reaper needs
versioned namespace ownership, exact file type and inode evidence, age, and
preferably process-incarnation or lease evidence. It must never infer ownership
from a recognizable filename alone.

This revision still does not provide the project's missing distributed
convergence algebra, disposable hostile-database worker, or complete payload
confidentiality, metadata-leakage, device enrollment, key rotation, revocation,
recovery, forward-secrecy, and post-compromise-recovery design.
