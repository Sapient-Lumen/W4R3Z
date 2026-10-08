# Rev0828 audit — durable reset plus immutable publication

## Mission-level finding

AnonSync's core discipline is that observation is not authority. Rev0827 left a
critical proof gap between two individually strong owners: the reset transaction
could become durable before receipt publication, while tests could observe only
the reset side or invoke publication as a separate success-path operation.
Correct local components did not yet amount to an executable cross-resource
recovery protocol.

Rev0828 does not pretend to make SQLite and the filesystem one atomic
transaction. It instead exposes every application-owned frontier, records the
strongest fact established there, and proves exact recovery without destroying
objects whose ownership is unknown.

## Production refactor

`SyncPreparedImmutableJsonPublication::publish_or_throw()` now delegates to one
internal `PreparedImmutableJsonPublicationObserverAccess`. The access class is a
friend of the move-only capability and receives the exact object prepared before
the SQLite transition. It moves the implementation out before validation, so
success, typed failure, observer exception, stale process incarnation, and
invalid capability all preserve single-use semantics.

The observer type remains in the internal header. The public header exposes only
an incomplete friend declaration, adding no public observer overload. Both
Windows and POSIX platform calls receive the observer and the existing progress
state. The existing prepared-publication test remains byte- and behavior-level
coverage of the same implementation.

## Combined process oracle

The Linux-only focused executable uses real `fork()` and `_exit()` rather than
simulating process death with a caught exception. The child owns the prepared
parent-directory descriptor, commits the real reset, and exits at:

1. the durable reset observation before publication starts; and
2. each of the 11 publication observations from temp reservation through parent
   descriptor closure.

The parent waits for an exact exit status, reopens SQLite, verifies the durable
empty state, inspects receipt/temp namespace effects, and performs exact replay
to a distinct fresh output path. Separate caught-failure cases verify the typed
outcome/residue pair and consumed capability at all 11 frontiers.

Adversarial cases replace the receipt parent after commit or create a competing
final object after commit. Publication fails closed without writing into the old
or replacement parent, replacing the competitor, or manufacturing cleanup
authority. Unknown temp residue is preserved by device/inode/size/byte identity.
Already-published evidence is preserved by inode and byte identity.

Direct result: **357 checks**. Twenty-five consecutive executions passed
**8,925 assertions**.

## Refactor and waste audit

The original reset test embedded its own SQLite RAII, schema creation, ledger
seed, expectation projection, and request construction. Rev0828 extracts that
256-line fixture into a test-only header shared by the reset and cross-frontier
executables. No fixture code enters a production library, and the combined test
is configure-time forbidden from linking `anonsync_core_lib`.

The extraction exposed a constructor-unwind leak: after a successful
`sqlite3_open_v2`, failure of `sqlite3_busy_timeout` threw before the destructor
could run. The fixture now closes and nulls the handle before throwing.

A separate performance suspicion was handled fail-closed. An indexed line-number
variant for the persistence inventory audit was benchmarked and was slightly
slower on this cube, so it was rejected and the original source restored. The
observed multi-minute interference came from stale worktrees launching orphaned
CTest processes, not from a proved algorithmic regression in the sealed source.

## Structural release obligations

- atomic publication audit: **39/39**;
- SQLite reset audit: **99/99**;
- combined crash-frontier audit: **18/18**;
- reset receipt audit: **40/40**;
- aggregate: **196/196**.

The new executable and audit are CTest obligations, sanitizer participants,
package-verifier requirements, and focused targets with an explicit no-core-link
guard.

## Claim boundary

The oracle kills a process at application-selected observations after the real
SQLite API returns. It does not intercept SQLite's VFS calls or emulate storage
reordering. Therefore it does not establish correctness for arbitrary failures
inside journal/WAL creation, `xWrite`, `xSync`, `xTruncate`, `xDelete`, directory
metadata persistence, torn sectors, kernel crashes, power loss, or dishonest
storage. It proves recovery classification for the frontiers it actually runs
and explicitly blocks broader claims.
