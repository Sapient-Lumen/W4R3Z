# OPFS block-store read-only no-create slice

Revision: rev0102  
Task: `opfs:block-store-readonly-no-create-proof`

This slice closes a concrete waste/hygiene bug in `OpfsAsyncBlockStore`: missing `get`, `has`, `verify`, and missing `delete` paths must not create empty OPFS prefix or bucket directories simply to discover `NotFoundError`.

Before this slice, `verify()` and related miss paths could reach the mutable `open()` path, which creates the configured prefix. Over time, cache probes, negative lookups, and cleanup checks could litter OPFS with empty directories and make later evidence harder to interpret.

The runtime now routes miss-prone read paths through no-create prefix/bucket opens. The `noCreateMisses` stat and `storage:opfs-block-no-create-miss` trace event expose the boundary. Real writes still use the mutable create path, and existing block `verify` / `has` / `get` / `delete` behavior remains unchanged.

The release proof uses the shared fake OPFS harness plus the new `createDirectoryMutationRecorder(...)` helper. It verifies that missing `verify`, verified `has`, unverified `has`, `delete`, and `get` leave the fake OPFS tree with zero directories and zero files, while a seeded existing block can still be written, verified, read, and deleted.

Non-claims: this is not recursive empty-directory compaction, not quota or eviction survival, not fsync durability, not crash or power-loss recovery, not cross-browser conformance, and not a production-readiness claim.
