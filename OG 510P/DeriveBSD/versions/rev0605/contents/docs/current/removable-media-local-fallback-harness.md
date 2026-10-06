# Current removable-media local-fallback harness

This cut keeps the removable-media first lane executable instead of only modeled.

`tools/removable_media_safe_capture.py` is the shared capture helper for the executable lane. It starts from a broker-owned media-root fd, walks each ancestor with dirfd/openat plus no-follow semantics, opens the selected leaf read-only with no-follow semantics, requires a regular file, verifies lstat/fstat object stability, records source stability through copy, writes a digest-addressed preserved copy, and verifies the stored copy. Its deterministic guard is:

- `tools/check_removable_media_safe_capture.py`
- `validation/removable-media-safe-capture.receipt.json`

`tools/run_removable_media_local_fallback_prototype.py` is still the no-root userland prototype that creates hostile members, rejects traversal/absolute/directory/symlink subjects, captures one regular file into a digest-addressed store, deletes the source media tree before the worker starts, and launches the later worker with preopened input/output descriptors rather than a live media path. It now uses the shared safe-capture helper and records symlink-ancestor rejection. Its deterministic receipt remains:

- `validation/removable-media-local-fallback-prototype-run.receipt.json`

`tools/removable_media_local_fallback_harness.py` is the canonical-fixture bridge. It runs against the checked-in `invoice.pdf` fixture, verifies that the real bytes match `spec/examples/content.import.plan.removable-media-local-ingest.json`, writes a preserved capture and a separate metadata-only derivative, and emits `removable.media.local.fallback.harness.run` evidence. Its expected output is:

- `spec/examples/removable.media.local.fallback.harness.run.json`
- `validation/removable-media-local-fallback-harness/expected/removable.media.local.fallback.harness.run.json`
- `validation/removable-media-local-fallback-harness/expected/store/sha256/01/01a0cd0826db2a58f930defd65189517c567703c224d715abefeb66897a5e2cc/preserved-subject.bin`
- `validation/removable-media-local-fallback-harness/expected/store/sha256/e6/e63a59cae69a31520a1103bbd0005930289bd8a146c579902a3c947998396169/sanitized-summary.json`

The paired guard `tools/check_removable_media_local_fallback_harness_run.py` replays the harness, compares the generated evidence to the canonical example, verifies the stored evidence file digests and sizes, and checks closed failures for an unknown filesystem family, a `..` path escape, a directory subject, and symlink components anywhere in the selected subject path. It also keeps the post-detach worker surface constrained: no live ingest mount, no media mount, no device nodes, no socket descriptors, one single-object projection digest, and one separate derivative output.

The harness is not a production FreeBSD mounter, jail launcher, or Capsicum proof. It is the smallest replayable cloudtainer proof that the current capture-first and post-detach worker story can be driven from actual bytes, that the selected subject is opened through a pinned no-symlink path walk, and that placeholder subject digests are no longer carrying this lane.

2026-06-16r572 fixture correction: `invoice.pdf` is a valid visible deterministic PDF bound to `sha256:01a0cd0826db2a58f930defd65189517c567703c224d715abefeb66897a5e2cc`, and the expected preserved capture / sanitized summary outputs were regenerated from those bytes.

Last updated: 2026-06-16r572
