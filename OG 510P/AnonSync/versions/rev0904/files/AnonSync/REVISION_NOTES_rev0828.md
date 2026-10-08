# AnonSync rev0828 — cross-frontier recovery, exact prepared observer, residue proof

Rev0828 joins two previously isolated invariant owners into one executable
application recovery protocol: durable SQLite reset and immutable receipt
publication.

The production refactor is deliberately small. An internal friend access point
can attach a deterministic observer to the exact move-only prepared publication
capability. Public `publish_or_throw()` delegates to that same implementation
with a null observer; there is no test-only publisher. Authority is moved out of
the caller before validation, remains single-use on every return path, and the
observer is forwarded through both platform implementations without entering
the public API.

The new Linux process oracle prepares the final-path capability before the
irreversible reset, commits the real SQLite transaction, and then exercises:

- the post-commit/pre-publication crash gap;
- all 11 prepared-publication process-exit frontiers;
- all 11 corresponding caught typed-failure frontiers;
- parent-directory replacement after commit;
- a competing final receipt after commit; and
- exact recovery to a distinct fresh receipt name.

For every frontier the parent reopens the database, verifies the deterministic
empty state and receipt digest, classifies namespace effects, and preserves
unowned objects. Pre-publication temp residue must retain the same device,
inode, size, and bytes after recovery. A published immutable receipt must retain
its inode and canonical bytes. Recovery therefore proves what it owns rather
than deleting a guessed temp name or replacing a first publisher.

The reset test's 256-line schema/seed/expectation fixture is now shared with the
combined oracle. During extraction, its SQLite constructor was corrected to
close the opened handle if `sqlite3_busy_timeout()` fails before construction
completes.

Final evidence:

- parent ZIP **25/25** and directory **21/21**;
- patch replay **193/193 active files**;
- source delta **11 files, 1,462 insertions, 238 deletions**;
- all-target GCC 14 Debug build and final no-work closure: passed;
- complete CTest inventory **115/115** in three disjoint final-source ranges;
- focused final CTest **7/7**;
- direct combined oracle **357/357**;
- stress **25/25**, totaling **8,925 assertions**;
- structural audits **196/196**;
- Clang 17 `-Werror` **3/3**; and
- GCC 14 ASan/UBSan **3/3** with leak detection enabled.

A single uninterrupted 115-test invocation is deliberately not claimed. Two
aggregate attempts were interfered with by stale worktrees; the exact inventory
then passed as ranges 1–40, 41–80, and 81–115. A proposed inventory-audit
optimization was benchmarked, found slightly slower, and rejected rather than
sealing an unsupported performance claim.

Rev0828 proves process exit/reopen at selected application frontiers. It does
not prove arbitrary SQLite VFS I/O failure, torn writes, power loss, storage
ordering, Windows behavior, or cross-resource atomicity. Those limits are
release-gated facts, not footnotes.
