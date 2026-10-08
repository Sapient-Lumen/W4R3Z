# Atomic replace without directory sync

Simulates a crate that writes a config or snapshot through a temporary file and atomically replaces the destination.
The save path is safer than a naive in-place overwrite, but the contract still should **not** overclaim full durability.

Why this matters:
- `tempfile::NamedTempFile::persist` says replacement is atomic, but also says neither the file contents nor the containing directory are synchronized when `persist` returns.
- A persistence-surface crate should therefore distinguish **replacement semantics** from **durability boundary**.

What this scenario should force:
- `write_class = tempfile_replace`
- explicit write-path steps rather than one vague `save_succeeded`
- a downgraded durability boundary when directory/file sync evidence is absent
- a doctor warning such as `atomic_replace_without_sync_boundary`
