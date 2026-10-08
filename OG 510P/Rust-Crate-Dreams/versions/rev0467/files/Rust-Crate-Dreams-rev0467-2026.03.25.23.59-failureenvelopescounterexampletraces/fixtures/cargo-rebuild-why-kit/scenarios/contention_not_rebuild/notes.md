# contention_not_rebuild

A run waits on a shared root and then completes, but the interesting story is primarily **blocking**, not a rich rebuild-cause chain.

This scenario exists so the rebuild kit can preserve a contention hint without swallowing the lock-contention lane.
