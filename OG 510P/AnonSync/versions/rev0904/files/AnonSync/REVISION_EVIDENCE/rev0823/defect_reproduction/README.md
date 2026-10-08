# Live-backup defect evidence

`parent-unbounded-live-copy.json` is a source-level differential against the exact rev0822 parent. It records the separate early geometry observation and the later `sqlite3_backup_step(..., -1)` effect.

`backup_probe.c` is an independent SQLite API probe. It begins a source read transaction, performs a read that pins a 50-page snapshot, copies one page per online-backup step, and commits a separate WAL writer that grows the live source to 1,029 pages. `backup_probe.out` shows that the backup remains on the pinned 50-page image and the destination contains only the pre-writer row. The compiled probe binaries are deliberately excluded.

The probe supports the selected design but is not a substitute for the production executable or CTest gates.
