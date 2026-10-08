# Rev0819 pathname-deletion inventory

The repository-wide lexical pass found **480 candidate source lines** under `src/`:

- `9` raw POSIX `unlink`/`unlinkat` candidates;
- `164` C `remove` candidates;
- `259` `std::filesystem::remove` candidates; and
- `48` `std::filesystem::remove_all` candidates.

The intentionally crude surface classifier labels 92 candidates runtime and 388 selftest. A lexical hit is **not** automatically a defect. Each site needs an invariant-owner review: what exact object is authorized for deletion, which observation establishes that authority, and can the name be rebound between observation and deletion?

The corrected atomic publisher contains no production pathname-deletion call.
The next high-return reviews are `src/persistence/sqlite_snapshot_seal.cpp`
(four raw unlinks of staged SQLite artifacts) and `src/replay_ledger.cpp` (five
raw unlinks across journal/temp recovery). `src/sqlite_replay_ledger.cpp` also
has a large mixed runtime/selftest deletion surface and should be split before
its results are treated as architectural counts.

The complete record, including file, line, lexical kind, crude surface, and
source text, is in `inventory/pathname-deletion-inventory.json`.
