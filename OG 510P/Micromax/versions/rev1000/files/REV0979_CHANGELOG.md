# Rev0979 changelog — full-frame worker deadlines and large-buffer dirty cost

## One-shot worker transport

- Added a shared private `socketpair` result channel with an explicit magic and
  unsigned-length frame, nonblocking parent reads, one absolute deadline, and a
  finite result ceiling checked before payload growth.
- Added one collector for process start, parent-writer release, incremental
  receive, exact trusted-pickle decode, reap/terminate/kill, optional clean-exit
  policy, abnormal cleanup, endpoint closure, and process-handle release.
- Replaced one-shot Queue result paths in filesystem reads/metadata/listing,
  save planning/writes/cleanup, plugin fingerprint/snapshots, docs indexing, and
  project scanning.
- Replaced the regex compatibility `Pipe.recv()` path, which shared the same
  readiness-then-block framing weakness.
- Preserved caller-specific timeout, containment, result-shape, and cleanup
  behavior while giving each family a purpose-sized serialized-result ceiling.

## Large-buffer typing

- Added a visible, reversible buffer-local `fastdirty=true` policy for saved
  baselines at or above 1 MiB, avoiding an exact full-document hash after every
  edit by default.
- Kept exact return-to-clean semantics for ordinary buffers and for users who
  explicitly run `setlocal fastdirty false`.
- Encoded large exact signatures in 64 KiB chunks after a native line join,
  avoiding one full-document byte string without slowing the explicit exact
  path.
- Removed an initially overengineered per-line Python signature walker after the
  audit measured a 10–17× regression; final exact-mode speed remains near
  rev0978 while the default large-buffer edit path is constant-time dirty state.

## Audit and documentation

- Strengthened `mxaudit` against legacy Queue/Pipe result receives, missing
  full-frame deadline enforcement, late size checks, and hidden large-buffer
  dirty policy.
- Added adversarial transport, lifecycle, subsystem integration, signature, and
  reversible-option tests.
- Added `docs/936-worker-full-frame-deadline-large-buffer-fastdirty.md` with the
  measured failure, CPython source analysis, micro precedent, implementation,
  evidence, and residual risks.
- Updated current mission, roadmap, decisions, security boundary, worklist,
  revision index, README, TODO, and generated context. The context now keeps
  every current-revision code surface while capping stable code pointers at 64.
- Rotated rev0973 and rev0974 evidence into `docs/history/` to preserve the
  fixed curated context budget while retaining the expanded fast-dirty help.
- Compressed established decisions D1–D12 instead of raising the living-doc
  ceiling, preserving the decisions while deleting repetitive doctrine.
