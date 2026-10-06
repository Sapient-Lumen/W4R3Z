# OPFS block-store AbortSignal contract audit slice

`facility:opfs-block-store-abort-signal-contract-audit` is the current-office audit for rev0095.  It checks the runtime abort-signal needles in `src/opfs-block-store.mjs`, the public TypeScript declarations, the new release and browser probes, the docs, manifest rows, impact map, surface inventory, package scripts, and Makefile routing.

The audit also covers the small refactor that moved the fake OPFS classes into `tools/lib/fake_opfs_harness.mjs`.  The existing corrupt-block repair proof and the new abort-signal proof now share the same fake directory/file/writable-stream model instead of carrying separate in-file fake OPFS implementations.

This audit is wiring evidence only.  Behavior evidence comes from `opfs:block-store-abort-signal-proof` and `browser:opfs-block-store-abort-signal-proof`; the slice still makes no storage-lane timeout cancellation, fsync durability, crash safety, quota/eviction, cross-browser, or production-readiness claim.

Audit marker: not storage-lane timeout cancellation.
