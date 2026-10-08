# Complete CTest gate shape

The final CTest inventory contains 115 tests. It was executed against one final
source/build graph in three disjoint ranges:

- tests 1–40: 40 passed, 0 failed;
- tests 41–80: 40 passed, 0 failed;
- tests 81–115: 35 passed, 0 failed.

Together these logs cover every inventory index exactly once: **115/115**.

Two attempts to run the whole inventory in one uninterrupted command were
interfered with by stale parallel worktrees and their orphaned CTest processes.
Those roots/process groups were removed. Individual tests that appeared near the
interruption point passed in isolation and in the disjoint ranges. Because the
single-command condition was not cleanly established, this revision explicitly
sets `single_uninterrupted_complete_ctest` to false and does not use it as a
required release claim.
