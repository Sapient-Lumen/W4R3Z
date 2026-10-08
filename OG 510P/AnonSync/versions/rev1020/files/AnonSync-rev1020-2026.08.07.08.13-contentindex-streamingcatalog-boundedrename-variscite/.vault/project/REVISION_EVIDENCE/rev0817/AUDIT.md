# Rev0817 audit: ownership of atomic file publication

## Audit question

Can two valid AnonSync writers publish the same serialized payload to the same
report path without sharing, deleting, or renaming one another's temporary
object—and can the owner state precisely distinguish pre-publication cleanup
from post-publication durability uncertainty?

Rev0816 could not. Its temp suffix was a function of PID and payload digest.
Every same-process writer of the same payload therefore addressed one pathname.
Each caller also removed that pathname as presumed stale before exclusive
creation and again after failure. Under concurrency, a writer could unlink the
name of an inode another writer still held, create a replacement under the same
name, or consume that name by rename. The reproduced outcome was 129 failed
calls out of 144, with both `EEXIST` at creation and `ENOENT` at rename.

## Corrected authority model

The publication owner now has three separately evidenced objects:

1. a pinned parent-directory descriptor whose `fstat` identity is matched to a
   non-symlink terminal path observed by `lstat`;
2. a uniquely reserved temporary pathname created relative to that descriptor
   with `O_CREAT|O_EXCL`, private mode 0600, process identity, and a monotone
   per-call nonce; and
3. the temporary inode identity observed by `fstat` and revalidated through
   `fstatat(..., AT_SYMLINK_NOFOLLOW)` immediately before rename.

Cleanup is authorized only before the rename linearization point and only while
the pathname still names the exact device/inode pair created by this call. No
guessed stale file is removed. After rename, failure to sync or close is
reported as already-published bytes with indeterminate durability; the code does
not attempt path cleanup after authority moved to the final name.

## Directory binding finding

The cloudtainer runs Linux 4.4 on overlayfs. A focused probe observed that
`open(path, O_RDONLY|O_DIRECTORY|O_NOFOLLOW)` succeeded for a terminal directory
symlink in this environment. The implementation therefore does not treat flags
as proof. It first rejects a terminal symlink through `lstat`, then opens the
directory and proves `st_dev/st_ino` equality between the path observation and
descriptor. An identity change during that interval is rejected.

## Refactor result

The 592-line owner and 24-line API were extracted from `sync_domain.cpp` into
`anonsync_sync_atomic_file_publication`. Heartbeat and CLI report publication
now share that owner. CMake prevents the focused source from reentering the core
source list and prevents the focused library/test from acquiring a reverse core
dependency. A 20-check source audit binds implementation, callers, tests,
sanitation lanes, CTest registration, and package-verifier inclusion.

The exact parent race harness now changes from 129/144 exceptions to 0/144. The
focused executable passes 23/23 checks and 25 consecutive repetitions, covering
same-payload threads, distinct-payload linearization, forked writers, final
symlink and non-regular rejection, terminal parent symlink rejection, effective
0600 mode, preservation of the legacy deterministic temp path, CLI delegation,
and absence of module temp residue.

## Limits

Atomic rename is a local visibility linearization point; it is not a distributed
last-writer policy, a convergence algebra, or proof of durable recovery after
every crash cut. Directory `fsync` is requested after rename, but the correct
next test owner is an I/O/crash oracle that injects failure at create, write,
file sync, identity check, rename, directory sync, and close, then classifies
recovery as old bytes, complete new bytes, or explicitly indeterminate.

A principal with arbitrary create/unlink/rename rights in the trusted directory
can still interfere between identity revalidation and rename. This revision
prevents accidental same-principal writers from stealing one another's object
and rejects observed replacement; it does not claim a hostile shared-directory
sandbox.
