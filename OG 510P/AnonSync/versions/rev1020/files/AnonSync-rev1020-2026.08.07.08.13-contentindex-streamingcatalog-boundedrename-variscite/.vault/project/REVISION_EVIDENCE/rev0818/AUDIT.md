# Rev0818 audit

## Boundary selected

The audit selected atomic JSON publication because rev0817 had corrected temp
name ownership but still represented the protocol only as syscall control flow.
There was no executable state owner for retry authority, no deterministic crash
frontier, and no proof that every parent path component was link-free.

## Findings corrected

1. **Intermediate symlink traversal.** Rev0817 checked only the terminal parent.
   The sealed-parent differential proves that an intermediate symlink redirected
   a supposedly no-symlink publication. Rev0818 walks from `/` one component at
   a time with `fstatat(AT_SYMLINK_NOFOLLOW)`, `openat(O_NOFOLLOW|O_DIRECTORY)`,
   and exact device/inode comparison.
2. **Implicit effect state.** Errors had to be interpreted from timing or text.
   A separate allocation-free state owner now classifies not-published,
   published-with-directory-durability-indeterminate, and published-and-
   directory-synced outcomes. Rename and directory sync advance state before
   callbacks or diagnostics.
3. **False-success rebind window.** The configured parent is re-proven before
   rename and again after the pinned directory is synced. A deterministic late
   rebind now throws with the already-published-and-synced outcome rather than
   returning success for a file reachable only through the detached directory.
4. **Stale typed exception authority.** An already-typed nested error used to
   bypass recomposition. Every escaping runtime failure is now wrapped from the
   current state, while the original typed error remains nested evidence.
5. **Mutable temp security attributes.** Before rename, rev0818 re-proves exact
   inode identity, one-link exclusivity, and no group/other permission bits. A
   forced chmod widening is rejected and the exact writer-owned name is cleaned.

## Proof surface

- pure state test: 20/20;
- race/path runtime test: 28/28;
- exception and process-exit cutpoint test: 133/133;
- structural audit: 30/30;
- 25 consecutive focused repetitions;
- complete project gate: 96/96;
- GCC 14 and Clang 17 warning-as-error lanes;
- Clang 17 ASan/UBSan focused lane with leak detection disabled.

## Explicit limits

The pre/post parent checks are point-in-time evidence, not a lock on the
namespace. An uncoordinated principal can always rebind after the final check.
The process-exit corpus establishes namespace state at reviewed user-space
frontiers; it does not emulate power loss, storage-controller reordering, torn
writes, filesystem bugs, or every failing syscall. Windows behavior was not
executed in this Linux cloudtainer.
